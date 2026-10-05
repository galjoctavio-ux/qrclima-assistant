'use strict';
// Integration against actual Firestore/Auth/Storage emulators. Fails closed outside demo.
const assert = require('node:assert/strict');
const admin = require('firebase-admin');
const {randomBytes} = require('node:crypto');
const {createBridge} = require('../core');
const p = require('../policy');
const project = process.env.GCLOUD_PROJECT;
if (project !== 'demo-qrclima-assistant' || !['FIRESTORE_EMULATOR_HOST','FIREBASE_AUTH_EMULATOR_HOST','FIREBASE_STORAGE_EMULATOR_HOST']
  .every(key=>/^127\.0\.0\.1:\d+$/.test(process.env[key] || ''))) throw Error('LOCAL_DEMO_EMULATORS_ONLY');
admin.initializeApp({projectId:project,storageBucket:`${project}.appspot.com`});
const db=admin.firestore(), auth=admin.auth(), bucket=admin.storage().bucket();
let now=Date.now(), count=0;
const bridge=createBridge({db,auth,bucket,clock:()=>now});
const cases=async(name,fn)=>{await fn();count++;process.stdout.write(`PASS ${name}\n`);};
const reject=async(fn,code)=>assert.rejects(fn,error=>error instanceof p.BridgeError && (!code || error.code===code));
const credential=()=>randomBytes(32).toString('base64url');
async function grant(secret,uid='user_a',scopes=['business.read','profile.write','branding.write','documents.write']) {
  return bridge.browser(uid,Math.floor(now/1000),{action:'approve',organizationId:uid==='user_b'?'org_b':'org_a',requestId:p.hash(secret),scopes,label:'Synthetic assistant'});
}
async function main() {
  for(const uid of ['user_a','user_b','admin_a']) await auth.createUser({uid});
  await db.doc('users/user_a').set({organizationId:'org_a',role:'owner',active:true,displayName:'Synthetic A',city:'A'});
  await db.doc('users/user_b').set({organizationId:'org_b',role:'owner',active:true,displayName:'Synthetic B'});
  await db.doc('users/admin_a').set({organizationId:'org_a',role:'admin',active:true});
  await db.doc('organizations/org_a').set({ownerId:'user_a',plan:'pro_plus',name:'Synthetic A',pdfBranding:{footerText:'preserve'},cfdi:{emisorRfc:'DEMO010101AAA'}});
  await db.doc('organizations/org_b').set({ownerId:'user_b',plan:'pro_plus',name:'Synthetic B'});
  await db.doc('org_memberships/admin_a').set({memberships:{org_a:{role:'admin'}}});
  await db.doc('clients/a').set({organizationId:'org_a',name:'Client A',phone:'0000000000',internalSecret:'excluded'});
  await db.doc('clients/b').set({organizationId:'org_b',name:'Client B'});
  const key=credential(); await grant(key);
  await cases('unauthorized approval cannot select another organization',()=>reject(()=>bridge.browser('user_a',Math.floor(now/1000),{action:'approve',organizationId:'org_b',requestId:p.hash(credential()),scopes:['business.read']}),'permission_denied'));
  await cases('read only returns the bound organization',async()=>{
    const result=await bridge.connector(key,{action:'read',category:'clients'});
    assert.deepEqual(result.records.map(v=>v.id),['a']);assert.equal(result.records[0].internalSecret,undefined);
  });
  await cases('organization and raw collection injection rejected',async()=>{
    await reject(()=>bridge.connector(key,{action:'read',category:'clients',organizationId:'org_b'}),'invalid_argument');
    await reject(()=>bridge.connector(key,{action:'read',category:'org_secrets'}),'invalid_argument');
  });
  await cases('profile write rereads saved fields and preserves organization',async()=>{
    const before=await bridge.connector(key,{action:'status'});
    const input={action:'update_profile',patch:{city:'Changed City'},expectedRevision:before.profileRevision,requestId:'profile_1',confirmed:true};
    await bridge.connector(key,input);
    const after=await bridge.connector(key,{action:'status'});assert.equal(after.profile.city,'Changed City');
    assert.notEqual(after.profileRevision,before.profileRevision);assert.equal(after.organizationId,'org_a');
    const replay=await bridge.connector(key,input);assert.equal(replay.replayed,true);
    await reject(()=>bridge.connector(key,{...input,patch:{city:'Other City'}}),'conflict');
    assert.equal((await db.doc('users/user_b').get()).get('displayName'),'Synthetic B');
  });
  await cases('missing confirmation, role field and stale revision rejected',async()=>{
    await reject(()=>bridge.connector(key,{action:'update_profile',patch:{city:'X'},requestId:'x'}),'confirmation_required');
    await reject(()=>bridge.connector(key,{action:'update_profile',patch:{role:'owner'},confirmed:true,requestId:'x'}),'invalid_argument');
    await reject(()=>bridge.connector(key,{action:'update_profile',patch:{city:'X'},confirmed:true,expectedRevision:'stale',requestId:'x'}),'conflict');
  });
  await cases('branding preserves other nested fields',async()=>{
    const before=await bridge.connector(key,{action:'status'});
    await bridge.connector(key,{action:'update_branding',patch:{primaryColor:'#123456'},confirmed:true,expectedRevision:before.organizationRevision,requestId:'brand_1'});
    const after=await bridge.connector(key,{action:'status'});
    assert.equal(after.organization.pdfBranding.footerText,'preserve'); assert.equal(after.organization.pdfBranding.primaryColor,'#123456');
  });
  let documentId;
  await cases('constancia saved privately with tenant metadata and replay protection',async()=>{
    const input={action:'upload',kind:'constancia',name:'test.pdf',contentBase64:Buffer.from('%PDF-1.4\nSynthetic PDF').toString('base64'),requestId:'document_1',confirmed:true};
    const result=await bridge.connector(key,input);documentId=result.documentId;
    const metadata=await db.doc(`assistant_documents/${documentId}`).get();assert.equal(metadata.get('organizationId'),'org_a');
    const [object]=await bucket.file(metadata.get('path')).getMetadata();assert.equal(object.metadata?.firebaseStorageDownloadTokens,undefined);
    const replay=await bridge.connector(key,input);assert.equal(replay.replayed,true);
    const download=await bridge.connector(key,{action:'download',documentId});assert.equal(download.contentBase64,input.contentBase64);
  });
  const keyB=credential();await grant(keyB,'user_b');
  await cases('other organization cannot download document by guessed ID',()=>reject(()=>bridge.connector(keyB,{action:'download',documentId}),'not_found'));
  await cases('profile image updates only its owner and stored reference',async()=>{
    const before=await bridge.connector(key,{action:'status'});
    const png=Buffer.from([137,80,78,71,13,10,26,10,0,0,0,0]);
    await bridge.connector(key,{action:'upload',kind:'profile_photo',name:'test.png',contentBase64:png.toString('base64'),confirmed:true,requestId:'photo_1',expectedRevision:before.profileRevision});
    const after=await bridge.connector(key,{action:'status'});assert.match(after.profile.photoURL,/profile_photos%2Fuser_a_assistant_/);
    assert.equal((await db.doc('users/user_b').get()).get('photoURL'),undefined);
  });
  const readOnly=credential();await grant(readOnly,'user_a',['business.read']);
  await cases('read-only grant cannot write or upload',async()=>{
    await reject(()=>bridge.connector(readOnly,{action:'update_profile',patch:{city:'x'},confirmed:true}),'permission_denied');
    await reject(()=>bridge.connector(readOnly,{action:'upload',kind:'constancia',name:'test.pdf',contentBase64:Buffer.from('%PDF-x').toString('base64'),requestId:'read_only_1',confirmed:true}),'permission_denied');
  });
  await cases('revocation immediately denies reads and writes',async()=>{
    await bridge.browser('user_a',Math.floor(now/1000),{action:'revoke',organizationId:'org_a',requestId:p.hash(readOnly)});
    await reject(()=>bridge.connector(readOnly,{action:'status'}),'unauthenticated');
  });
  await cases('disabled Auth identity immediately denied',async()=>{
    await auth.updateUser('user_b',{disabled:true});await reject(()=>bridge.connector(keyB,{action:'status'}),'permission_denied');await auth.updateUser('user_b',{disabled:false});
  });
  await cases('changing active organization invalidates previous grant',async()=>{
    await db.doc('users/user_a').update({organizationId:'org_b'});await reject(()=>bridge.connector(key,{action:'status'}),'permission_denied');await db.doc('users/user_a').update({organizationId:'org_a'});
  });
  await cases('admin removal invalidates connection',async()=>{
    const keyAdmin=credential();await grant(keyAdmin,'admin_a',['business.read']);
    await db.doc('org_memberships/admin_a').set({memberships:{}});await reject(()=>bridge.connector(keyAdmin,{action:'status'}),'permission_denied');
  });
  await cases('deletion fence stops new operations',async()=>{
    await db.doc('organizationDeletionFences/org_a').set({state:'closed'});await reject(()=>bridge.connector(key,{action:'status'}),'permission_denied');await db.doc('organizationDeletionFences/org_a').delete();
  });
  await cases('private contacts from another tenant are never merged',async()=>{
    await db.doc('clients/a').update({phone:''});
    await db.doc('bot_client_private_contacts/a').set({organizationId:'org_b',clientId:'a',phone:'foreign-contact'});
    const result=await bridge.connector(key,{action:'read',category:'clients'});assert.equal(result.records[0].phone,'');
    await db.doc('bot_client_private_contacts/a').update({organizationId:'org_a',phone:'own-contact'});
    assert.equal((await bridge.connector(key,{action:'read',category:'clients'})).records[0].phone,'own-contact');
  });
  await cases('revocation during upload prevents linking and compensates only its object',async()=>{
    const temporaryKey=credential();await grant(temporaryKey);
    let created;
    const intercepted={name:bucket.name,file:path=>{
      const original=bucket.file(path);created=original;
      return {save:async(...args)=>{await original.save(...args);await db.doc(`assistant_connections/${p.hash(temporaryKey)}`).update({revokedAt:now});},
        getMetadata:(...args)=>original.getMetadata(...args),delete:(...args)=>original.delete(...args)};
    }};
    const interrupted=createBridge({db,auth,bucket:intercepted,clock:()=>now});
    await reject(()=>interrupted.connector(temporaryKey,{action:'upload',kind:'constancia',name:'test.pdf',contentBase64:Buffer.from('%PDF-Synthetic').toString('base64'),confirmed:true,requestId:'revoked_upload'}),'unauthenticated');
    assert.equal((await created.exists())[0],false);
    assert.equal((await db.doc(`assistant_receipts/${p.hash(temporaryKey)}_revoked_upload`).get()).get('state'),'failed');
  });
  await cases('daily upload budget applies across connections of the same organization',async()=>{
    const quota=db.doc(`assistant_upload_quotas/org_a_${Math.floor(now/86400000)}`);await quota.set({count:20,bytes:1});
    const newKey=credential();await grant(newKey);
    await reject(()=>bridge.connector(newKey,{action:'upload',kind:'constancia',name:'test.pdf',contentBase64:Buffer.from('%PDF-budget').toString('base64'),confirmed:true,requestId:'budget_upload'}),'resource_exhausted');
    assert.equal((await db.doc(`assistant_receipts/${p.hash(newKey)}_budget_upload`).get()).exists,false);
  });
  await cases('connection expires without a local profile override',async()=>{
    now+=31*86400000;await reject(()=>bridge.connector(key,{action:'status'}),'unauthenticated');
  });
  process.stdout.write(`${count} emulator scenarios passed; synthetic data only.\n`);
}
main().then(()=>admin.app().delete()).catch(error=>{console.error(error);process.exitCode=1;});
