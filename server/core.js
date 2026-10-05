'use strict';
const {randomUUID} = require('node:crypto');
const p = require('./policy');
const {profileCompleteness} = require('./profile-completeness');
const DAY = 86400000;
const PROFILE = ['displayName','fullName','businessName','city','phone','photoURL','assistantRevision'];
const ORG = ['name','plan','type','timezone','assistantRevision'];
function createBridge({db, auth, bucket, clock = Date.now}) {
  const revision = snap => snap.updateTime ? `${snap.updateTime.seconds}:${snap.updateTime.nanoseconds}` : null;
  async function scope(tx, uid, orgId) {
    const [user, org, mem, userFence, orgFence, authUser] = await Promise.all([
      tx.get(db.doc(`users/${p.identifier(uid)}`)), tx.get(db.doc(`organizations/${p.identifier(orgId)}`)),
      tx.get(db.doc(`org_memberships/${uid}`)), tx.get(db.doc(`accountDeletionWriteBarriers/${uid}`)),
      tx.get(db.doc(`organizationDeletionFences/${orgId}`)), auth.getUser(uid),
    ]);
    if ((userFence.exists && userFence.get('state') !== 'open') || (orgFence.exists && orgFence.get('state') !== 'open'))
      p.fail('permission_denied', 'La cuenta o la organización está en proceso de eliminación.', 403);
    return {current: p.access(uid, user.data(), orgId, org.data(), mem.data(), authUser), user, org, authUser};
  }
  function publicState(s, grant) {
    return {uid: s.current.uid, organizationId: s.current.organizationId, owner: s.current.owner,
      profile: p.project(s.user.data(), PROFILE), profileRevision: revision(s.user),
      organization: {...p.project(s.org.data(), ORG), pdfBranding: p.project(s.org.get('pdfBranding') || {}, ['logoURL','footerText','primaryColor']),
        fiscal: p.project(s.org.get('cfdi') || {}, ['configured','emisorRfc','emisorRazonSocial','emisorRegimenFiscal','lugarExpedicion'])},
      organizationRevision: revision(s.org), ...(grant ? {scopes: grant.scopes, expiresAt: grant.expiresAt} : {})};
  }
  async function browser(uid, authTime, input) {
    p.exact(input, ['action','organizationId','requestId','scopes','label']);
    if (!['preview','approve','connections','revoke'].includes(input.action)) p.fail('invalid_argument', 'Acción inválida.');
    const orgId = p.identifier(input.organizationId);
    return db.runTransaction(async tx => {
      const s = await scope(tx, uid, orgId);
      if (input.action === 'preview') return publicState(s);
      if (input.action === 'connections') {
        const docs = await tx.get(db.collection('assistant_connections').where('uid','==',uid).limit(100));
        return {connections: docs.docs.filter(d => d.get('organizationId') === orgId).map(d => ({id: d.id,
          label: d.get('label'), scopes: d.get('scopes'), expiresAt: d.get('expiresAt'), revoked: !!d.get('revokedAt')}))};
      }
      const id = p.grantId(input.requestId), ref = db.doc(`assistant_connections/${id}`);
      const previous = await tx.get(ref);
      if (input.action === 'revoke') {
        if (!previous.exists || previous.get('uid') !== uid || previous.get('organizationId') !== orgId)
          p.fail('permission_denied', 'Conexión no disponible.', 403);
        tx.update(ref, {revokedAt: clock()});
        return {revoked: true};
      }
      if (previous.exists) p.fail('already_exists', 'Esta solicitud ya se utilizó. Inicia una nueva conexión.', 409);
      if (!Number.isFinite(authTime) || clock() - authTime * 1000 > 10 * 60000)
        p.fail('reauth_required', 'Por seguridad, vuelve a iniciar sesión para autorizar el asistente.', 401);
      const permissions = p.scopes(input.scopes, s.current.owner);
      const connections = await tx.get(db.collection('assistant_connections').where('uid','==',uid).limit(101));
      if (connections.size >= 100) p.fail('resource_exhausted', 'Se requiere depurar conexiones vencidas antes de agregar otra.', 429);
      if (connections.docs.filter(d => !d.get('revokedAt') && d.get('expiresAt') > clock()).length >= 10)
        p.fail('resource_exhausted', 'Revoca una conexión anterior antes de agregar otra.', 429);
      const grant = {uid, organizationId: orgId, scopes: permissions, label: p.text(input.label || 'Mi asistente', 80),
        createdAt: clock(), authTime: authTime * 1000, expiresAt: clock() + 30 * DAY, deleteAfter:new Date(clock() + 120 * DAY), revokedAt: null};
      tx.create(ref, grant);
      return publicState(s, grant);
    });
  }
  async function session(tx, secret, needed) {
    const id = p.secretId(secret), connection = await tx.get(db.doc(`assistant_connections/${id}`));
    const grant = connection.data();
    if (!grant || grant.revokedAt || grant.expiresAt <= clock()) p.fail('unauthenticated', 'Conexión pendiente, expirada o revocada.', 401);
    const s = await scope(tx, grant.uid, grant.organizationId);
    p.bound(grant, s.current, needed, clock());
    const invalidatedAt = Date.parse(s.authUser.tokensValidAfterTime || '1970-01-01');
    if (invalidatedAt > grant.authTime) p.fail('unauthenticated', 'La cuenta cerró sus sesiones. Vuelve a conectar.', 401);
    return {...s, grant, id};
  }
  async function rate(key, maximum, windowMs) {
    const ref = db.doc(`assistant_rate_limits/${p.hash(key + ':' + Math.floor(clock() / windowMs))}`);
    await db.runTransaction(async tx => {
      const snap = await tx.get(ref), count = snap.get('count') || 0;
      if (count >= maximum) p.fail('resource_exhausted', 'Se alcanzó el límite. Intenta más tarde.', 429);
      tx.set(ref, {count: count + 1, expiresAt: new Date(clock() + windowMs * 2)});
    });
  }
  async function connector(secret, input) {
    p.exact(input, ['action','category','cursor','limit','patch','expectedRevision','requestId','confirmed','kind','name','contentBase64','documentId']);
    const id = p.secretId(secret);
    // Bound anonymous polling and authenticated use separately in the HTTP wrapper.
    await db.runTransaction(tx => session(tx, secret, 'business.read'));
    await rate('connection:' + id, 60, 60000);
    await rate('daily:' + id, 1000, DAY);
    if (input.action === 'upload') return uploadFile(secret, input);
    if (input.action === 'download') return download(secret, input);
    return db.runTransaction(async tx => {
      const write = ['update_profile','update_branding'].includes(input.action);
      const needed = input.action === 'update_profile' ? 'profile.write' : input.action === 'update_branding' ? 'branding.write' : 'business.read';
      const s = await session(tx, secret, needed);
      if (input.action === 'status') return publicState(s, s.grant);
      if (input.action === 'disconnect') { tx.update(db.doc(`assistant_connections/${id}`), {revokedAt: clock()}); return {revoked: true}; }
      if (input.action === 'read') {
        const collection = p.COLLECTIONS[input.category], fields = p.FIELDS[input.category];
        if (!Object.hasOwn(p.COLLECTIONS,input.category)) p.fail('invalid_argument', 'Categoría no disponible.');
        const limit = input.limit ?? 50;
        if (!Number.isSafeInteger(limit) || limit < 1 || limit > 100) p.fail('invalid_argument', 'El límite debe estar entre 1 y 100.');
        let query = db.collection(collection).where('organizationId','==',s.current.organizationId).orderBy('__name__').limit(limit + 1);
        if (input.cursor) query = query.startAfter(p.identifier(input.cursor));
        const result = await tx.get(query), records = result.docs.slice(0,limit);
        const projected = [];
        for (const doc of records) {
          const data = doc.data();
          if (input.category === 'clients') {
            const contact = await tx.get(db.doc(`bot_client_private_contacts/${doc.id}`));
            if (contact.get('organizationId') === s.current.organizationId && contact.get('clientId') === doc.id)
              for (const field of ['phone','email','emailFiscal']) if (!data[field] && contact.get(field)) data[field] = contact.get(field);
          }
          projected.push({...p.project(data,fields), id:doc.id});
        }
        return {organizationId: s.current.organizationId, category: input.category, records: projected,
          nextCursor: result.size > limit ? records[records.length - 1].id : null, observedAt: clock(), coverage: 'page'};
      }
      if (!write) p.fail('invalid_argument', 'Acción no disponible.');
      if (input.confirmed !== true) p.fail('confirmation_required', 'Confirma los cambios concretos antes de guardarlos.');
      const requestId = p.identifier(input.requestId), ref = input.action === 'update_profile' ? s.user.ref : s.org.ref;
      if (needed === 'branding.write' && !s.current.owner) p.fail('permission_denied', 'Solo el propietario puede cambiar la marca.', 403);
      const patch = needed === 'profile.write' ? p.profilePatch(input.patch) : p.brandingPatch(input.patch);
      const receipt = db.doc(`assistant_receipts/${id}_${requestId}`), prior = await tx.get(receipt);
      const fingerprint = p.hash(JSON.stringify({action:input.action, patch, expectedRevision: input.expectedRevision}));
      if (prior.exists) {
        if (prior.get('fingerprint') !== fingerprint) p.fail('conflict', 'El identificador ya se utilizó con otros cambios.', 409);
        return {saved: true, replayed: true, receiptId: receipt.id, ...publicState(s, s.grant)};
      }
      const current = needed === 'profile.write' ? s.user : s.org;
      if (typeof input.expectedRevision !== 'string' || input.expectedRevision !== revision(current))
        p.fail('conflict', 'Los datos cambiaron. Consulta el estado y revisa el borrador.', 409);
      tx.update(ref, {...patch, ...(needed === 'profile.write' ? {profileCompletenessScore:profileCompleteness({...current.data(),...patch})} : {}),
        updatedAt: new Date(clock()), assistantRevision: (current.get('assistantRevision') || 0) + 1});
      tx.create(receipt, {fingerprint, uid:s.current.uid, organizationId:s.current.organizationId, action:input.action, createdAt:clock()});
      return {saved: true, receiptId: receipt.id, verification: 'Consulta status para releer el resultado.'};
    });
  }
  async function uploadFile(secret, input) {
    if (input.confirmed !== true) p.fail('confirmation_required', 'Confirma el archivo y su destino.');
    const data = p.upload(Object.fromEntries(Object.entries(input).filter(([key]) => !['action','confirmed'].includes(key))));
    const needed = data.kind === 'profile_photo' ? 'profile.write' : data.kind === 'organization_logo' ? 'branding.write' : 'documents.write';
    const id = p.secretId(secret), requestId = p.identifier(input.requestId);
    const receiptRef = db.doc(`assistant_receipts/${id}_${requestId}`);
    const fingerprint = p.hash(JSON.stringify({kind:data.kind,digest:data.digest,name:data.name,expectedRevision:input.expectedRevision}));
    const prepared = await db.runTransaction(async tx => {
      const s = await session(tx, secret, needed), prior = await tx.get(receiptRef);
      if (data.kind === 'organization_logo' && !s.current.owner) p.fail('permission_denied', 'Solo el propietario puede subir el logo.', 403);
      if (prior.exists) {
        if (prior.get('fingerprint') !== fingerprint) p.fail('conflict', 'El intento corresponde a otro archivo.', 409);
        if (prior.get('state') === 'completed') return {completed: true, receiptId:receiptRef.id, documentId:prior.get('documentId') || null};
        // Never silently repeat an external write with unknown completion.
        p.fail('outcome_unknown', 'La subida anterior requiere revisión; no generes otro intento.', 409);
      }
      const target = data.kind === 'profile_photo' ? s.user : s.org;
      if (data.kind !== 'constancia' && input.expectedRevision !== revision(target))
        p.fail('conflict', 'El perfil o la marca cambió. Consulta el estado.', 409);
      const quotaRef = db.doc(`assistant_upload_quotas/${s.current.organizationId}_${Math.floor(clock()/DAY)}`);
      const quota = await tx.get(quotaRef);
      if ((quota.get('count') || 0) >= 20 || (quota.get('bytes') || 0) + data.content.length > 50*1024*1024)
        p.fail('resource_exhausted', 'La organización alcanzó su límite diario de archivos.', 429);
      const documentId = randomUUID();
      const path = data.kind === 'profile_photo' ? `profile_photos/${s.current.uid}_assistant_${documentId}.${data.ext}`
        : data.kind === 'organization_logo' ? `orgs/${s.current.organizationId}/assistant-logo-${documentId}.${data.ext}`
        : `assistant_private_documents/${s.current.organizationId}/${documentId}.pdf`;
      tx.create(receiptRef, {fingerprint, state:'reserved', path, documentId, uid:s.current.uid,
        organizationId:s.current.organizationId, action:'upload', createdAt:clock()});
      tx.set(quotaRef, {count:(quota.get('count') || 0)+1, bytes:(quota.get('bytes') || 0)+data.content.length, deleteAfter:new Date(clock()+7*DAY)});
      return {s, path, documentId, completed:false};
    });
    if (prepared.completed) return {saved:true, replayed:true, ...prepared};
    const file = bucket.file(prepared.path), downloadToken = data.kind === 'constancia' ? null : randomUUID();
    let generation;
    try {
      // Unique object; precondition prevents an overwrite even if an attempt races.
      await file.save(data.content, {resumable:false, contentType:data.mime, preconditionOpts:{ifGenerationMatch:0},
        metadata:{metadata: downloadToken ? {firebaseStorageDownloadTokens:downloadToken} : {}}});
      const [meta] = await file.getMetadata(); generation = meta.generation;
      const result = await db.runTransaction(async tx => {
        const s = await session(tx,secret,needed), receipt = await tx.get(receiptRef);
        if (receipt.get('state') !== 'reserved' || receipt.get('fingerprint') !== fingerprint) p.fail('conflict', 'El intento cambió.', 409);
        const target = data.kind === 'profile_photo' ? s.user : s.org;
        if (data.kind !== 'constancia' && input.expectedRevision !== revision(target)) p.fail('conflict', 'Los datos cambiaron durante la subida.', 409);
        if (data.kind === 'constancia') tx.create(db.doc(`assistant_documents/${prepared.documentId}`), {
          organizationId:s.current.organizationId, uploadedBy:s.current.uid, path:prepared.path, name:data.name,
          kind:data.kind, size:data.content.length, mime:data.mime, createdAt:new Date(clock()), revision:1});
        else {
          const url = `https://firebasestorage.googleapis.com/v0/b/${encodeURIComponent(bucket.name)}/o/${encodeURIComponent(prepared.path)}?alt=media&token=${downloadToken}`;
          tx.update(target.ref, {[data.kind === 'profile_photo' ? 'photoURL' : 'pdfBranding.logoURL']:url,
            ...(data.kind === 'profile_photo' ? {profileCompletenessScore:profileCompleteness({...target.data(),photoURL:url})} : {}),
            updatedAt:new Date(clock()), assistantRevision:(target.get('assistantRevision') || 0) + 1});
        }
        tx.update(receiptRef, {state:'completed', generation, completedAt:clock()});
        return {saved:true, documentId:prepared.documentId, receiptId:receiptRef.id, verification:'Relee status o documents para comprobar.'};
      });
      return result;
    } catch (error) {
      // If saving Firestore succeeded but returning failed, preserve the linked file.
      const current = await receiptRef.get();
      if (current.get('state') === 'completed') return {saved:true, receiptId:receiptRef.id, documentId:prepared.documentId};
      if (generation) {
        await file.delete({ifGenerationMatch:generation});
        await receiptRef.update({state:'failed', failedAt:clock()});
      }
      throw error;
    }
  }
  async function download(secret, input) {
    const docId = p.identifier(input.documentId);
    const prepared = await db.runTransaction(async tx => {
      const s = await session(tx,secret,'business.read'), doc = await tx.get(db.doc(`assistant_documents/${docId}`));
      if (!doc.exists || doc.get('organizationId') !== s.current.organizationId) p.fail('not_found', 'Documento no disponible.', 404);
      const path = doc.get('path');
      if (path !== `assistant_private_documents/${s.current.organizationId}/${docId}.pdf`) p.fail('permission_denied', 'Referencia no válida.', 403);
      return {path, name:doc.get('name'), mime:doc.get('mime')};
    });
    const [content] = await bucket.file(prepared.path).download();
    if (content.length > 8 * 1024 * 1024) p.fail('resource_exhausted', 'Documento demasiado grande.', 413);
    // Recheck revocation/membership before releasing bytes after external I/O.
    await db.runTransaction(tx => session(tx,secret,'business.read'));
    return {name:prepared.name,mime:prepared.mime,contentBase64:content.toString('base64')};
  }
  return {browser, connector, rate};
}
module.exports = {createBridge};
