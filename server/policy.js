'use strict';
const {createHash} = require('node:crypto');
class BridgeError extends Error {
  constructor(code, message, status = 400) { super(message); this.code = code; this.status = status; }
}
const fail = (code, message, status) => { throw new BridgeError(code, message, status); };
const identifier = value => {
  if (typeof value !== 'string' || !/^[A-Za-z0-9_-]{1,128}$/.test(value)) fail('invalid_argument', 'Identificador inválido.');
  return value;
};
const hash = value => createHash('sha256').update(value).digest('hex');
const grantId = value => {
  if (typeof value !== 'string' || !/^[a-f0-9]{64}$/.test(value)) fail('invalid_argument', 'Solicitud inválida.');
  return value;
};
const secretId = value => {
  if (typeof value !== 'string' || !/^[A-Za-z0-9_-]{43}$/.test(value)) fail('unauthenticated', 'Conexión inválida.', 401);
  return hash(value);
};
const SCOPES = ['business.read', 'profile.write', 'branding.write', 'documents.write'];
function scopes(value, owner) {
  if (!Array.isArray(value) || !value.length || new Set(value).size !== value.length
      || value.some(v => !SCOPES.includes(v)) || (!owner && value.includes('branding.write')))
    fail('permission_denied', 'Permisos no disponibles para esta cuenta.', 403);
  if (!value.includes('business.read')) fail('invalid_argument', 'La conexión necesita lectura de su organización.');
  return value;
}
function access(uid, profile, orgId, org, member, authUser) {
  identifier(uid); identifier(orgId);
  if (!profile || profile.active === false || !org || org.active === false || authUser?.disabled
      || profile.organizationId !== orgId || profile.deletionStatus === 'pending' || org.deletionStatus === 'pending')
    fail('permission_denied', 'La cuenta ya no tiene acceso a esta organización.', 403);
  const owner = org.ownerId === uid && profile.role === 'owner';
  const admin = profile.role === 'admin' && member?.memberships?.[orgId]?.role === 'admin' && member.memberships[orgId].active !== false;
  if (!owner && !admin) fail('permission_denied', 'El piloto requiere propietario o administrador activo.', 403);
  if (!['pro_plus', 'enterprise'].includes(org.plan)) fail('permission_denied', 'Esta herramienta requiere Pro Plus o Enterprise.', 403);
  return {uid, organizationId: orgId, owner};
}
function bound(grant, current, needed, now = Date.now()) {
  if (!grant || grant.revokedAt || !Number.isFinite(grant.expiresAt) || grant.expiresAt <= now
      || grant.uid !== current.uid || grant.organizationId !== current.organizationId)
    fail('unauthenticated', 'La conexión expiró o fue revocada. Vuelve a conectarla.', 401);
  if (needed && !grant.scopes?.includes(needed)) fail('permission_denied', 'La conexión no tiene ese permiso.', 403);
  if (grant.scopes?.includes('branding.write') && !current.owner)
    fail('permission_denied', 'El permiso de propietario cambió. Vuelve a conectar.', 403);
}
function exact(value, allowed, required = []) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).some(k => !allowed.includes(k))
      || required.some(k => !(k in value))) fail('invalid_argument', 'Hay campos ausentes o no permitidos.');
  return value;
}
function text(value, maximum, blank = false) {
  if (typeof value !== 'string' || value.length > maximum || (!blank && !value.trim()) || /[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(value))
    fail('invalid_argument', 'Texto inválido.');
  return value.trim();
}
function profilePatch(input) {
  exact(input, ['displayName', 'fullName', 'businessName', 'city', 'phone']);
  if (!Object.keys(input).length) fail('invalid_argument', 'No hay cambios.');
  const out = {};
  for (const [key, value] of Object.entries(input)) out[key] = text(value, key === 'phone' ? 32 : 160, key === 'phone' || key === 'city');
  if (out.displayName && out.fullName && out.displayName !== out.fullName) fail('invalid_argument', 'El nombre no coincide.');
  if (out.fullName || out.displayName) out.displayName = out.fullName = out.fullName || out.displayName;
  return out;
}
function brandingPatch(input) {
  exact(input, ['name', 'footerText', 'primaryColor']);
  if (!Object.keys(input).length) fail('invalid_argument', 'No hay cambios.');
  const out = {};
  if ('name' in input) out.name = text(input.name, 160);
  if ('footerText' in input) out['pdfBranding.footerText'] = text(input.footerText, 2000, true);
  if ('primaryColor' in input) {
    if (!/^#[a-fA-F0-9]{6}$/.test(input.primaryColor)) fail('invalid_argument', 'Color inválido.');
    out['pdfBranding.primaryColor'] = input.primaryColor;
  }
  return out;
}
function upload(input) {
  exact(input, ['kind', 'contentBase64', 'name', 'expectedRevision', 'requestId'], ['kind', 'contentBase64', 'name', 'requestId']);
  identifier(input.requestId); const name = text(input.name, 160);
  const cap = input.kind === 'organization_logo' ? 2 * 1024 * 1024 : input.kind === 'constancia' ? 8 * 1024 * 1024 : 5 * 1024 * 1024;
  if (!['profile_photo', 'organization_logo', 'constancia'].includes(input.kind)
      || typeof input.contentBase64 !== 'string' || input.contentBase64.length > Math.ceil(cap / 3) * 4
      || input.contentBase64.length % 4 !== 0 || /[^A-Za-z0-9+/=]/.test(input.contentBase64)
      || /=/.test(input.contentBase64.slice(0,-2)) || input.contentBase64.endsWith('=') && !/[A-Za-z0-9+/](?:[A-Za-z0-9+/]=|==)$/.test(input.contentBase64.slice(-3)))
    fail('invalid_argument', 'Archivo inválido.');
  const content = Buffer.from(input.contentBase64, 'base64');
  if (content.toString('base64') !== input.contentBase64) fail('invalid_argument', 'Base64 no canónico.');
  if (!content.length || content.length > cap) fail('invalid_argument', 'El archivo supera el tamaño permitido.');
  let mime, ext;
  if (content.subarray(0, 8).equals(Buffer.from([137,80,78,71,13,10,26,10]))) { mime = 'image/png'; ext = 'png'; }
  else if (content[0] === 255 && content[1] === 216 && content[2] === 255) { mime = 'image/jpeg'; ext = 'jpg'; }
  else if (content.subarray(0, 5).toString('ascii') === '%PDF-') { mime = 'application/pdf'; ext = 'pdf'; }
  else fail('invalid_argument', 'Usa una imagen PNG/JPEG o un PDF para la constancia.');
  if ((input.kind === 'constancia') !== (ext === 'pdf')) fail('invalid_argument', 'El tipo de archivo no coincide con su destino.');
  return {content, name, mime, ext, digest: hash(content), kind: input.kind};
}
const FIELDS = {
  clients: ['name','fullName','phone','email','address','rfc','razonSocial','regimenFiscal','codigoPostal','emailFiscal','createdAt'],
  appointments: ['clientId','clientName','technicianId','technicianName','scheduledAt','date','endTime','durationMinutes','status','type','serviceType','description','address','sourceAppointmentId','createdAt'],
  concepts: ['code','name','description','unit','price','unitPrice','type','category','createdAt'],
  pro_concepts: ['code','name','description','unit','price','unitPrice','type','category','createdAt'],
  quotes: ['clientId','clientName','folio','status','total','subtotal','items','createdAt','validUntil'],
  pro_quotes: ['clientId','clientName','folio','status','total','subtotal','items','createdAt','validUntil'],
  sales: ['clientId','clientName','folio','status','total','amountPaid','items','date','createdAt'],
  documents: ['name','kind','size','mime','createdAt','revision'],
};
const COLLECTIONS = {clients: 'clients', appointments: 'services', concepts: 'cotizador_concepts', pro_concepts: 'pro_concepts',
  quotes: 'cotizador_quotes', pro_quotes: 'pro_quotes', sales: 'sales', documents: 'assistant_documents'};
function project(value, fields) {
  const encode = item => {
    if (item == null || typeof item !== 'object') return item;
    if (typeof item.toMillis === 'function') return new Date(item.toMillis()).toISOString();
    if (Array.isArray(item)) return item.map(encode);
    // Nested item details cannot smuggle credentials or unrelated arbitrary fields.
    const nested = ['id','name','description','quantity','unit','unitPrice','price','subtotal','total','type','conceptId'];
    return Object.fromEntries(Object.entries(item).filter(([key]) => nested.includes(key)).map(([key, v]) => [key, encode(v)]));
  };
  return Object.fromEntries(fields.filter(k => value[k] !== undefined).map(k => [k, encode(value[k])]));
}
module.exports = {BridgeError, fail, identifier, hash, grantId, secretId, scopes, access, bound, exact, text,
  profilePatch, brandingPatch, upload, FIELDS, COLLECTIONS, project};
