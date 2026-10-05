'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const p = require('../policy');
const {profileCompleteness} = require('../profile-completeness');
const owner = {organizationId:'org_a', role:'owner'};
const org = {ownerId:'user_a', plan:'pro_plus'};
const denied = fn => assert.throws(fn, error => error instanceof p.BridgeError);
test('ownership comes from server organization, not a supplied role', () => {
  assert.equal(p.access('user_a',owner,'org_a',org,{},{}).owner,true);
  denied(()=>p.access('user_b',owner,'org_a',org,{},{}));
});
test('organization switch, inactive user, disabled Auth and insufficient plan fail closed', () => {
  denied(()=>p.access('user_a',owner,'org_b',org,{},{}));
  denied(()=>p.access('user_a',{...owner,active:false},'org_a',org,{},{}));
  denied(()=>p.access('user_a',owner,'org_a',org,{}, {disabled:true}));
  denied(()=>p.access('user_a',owner,'org_a',{...org,plan:'free'}, {},{}));
});
test('administrator needs current server membership and cannot get owner permissions',()=>{
  const admin = {organizationId:'org_a',role:'admin'};
  denied(()=>p.access('admin_a',admin,'org_a',org,{},{}));
  assert.equal(p.access('admin_a',admin,'org_a',org,{memberships:{org_a:{role:'admin'}}},{}).owner,false);
  denied(()=>p.scopes(['business.read','branding.write'],false));
});
test('grant checks revocation, expiry, owner loss and missing operation scope',()=>{
  const current={uid:'user_a',organizationId:'org_a',owner:true};
  const grant={uid:'user_a',organizationId:'org_a',scopes:['business.read'],expiresAt:100};
  p.bound(grant,current,'business.read',10);
  denied(()=>p.bound({...grant,revokedAt:1},current,'business.read',10));
  denied(()=>p.bound(grant,current,'profile.write',10));
  denied(()=>p.bound(grant,{...current,organizationId:'org_b'},'business.read',10));
  denied(()=>p.bound(grant,current,'business.read',100));
  denied(()=>p.bound({...grant,scopes:['branding.write']},{...current,owner:false},'branding.write',10));
});
test('profile fields cannot change tenant, role, subscription, fiscal data or arbitrary URLs',()=>{
  for(const key of ['organizationId','uid','role','plan','subscription','photoURL','cfdi','__proto__'])
    denied(()=>p.profilePatch(JSON.parse(`{"${key}":"x"}`)));
  assert.deepEqual(p.profilePatch({city:'  Ciudad de prueba  '}),{city:'Ciudad de prueba'});
});
test('brand fields cannot replace nested settings or change entitlements',()=>{
  denied(()=>p.brandingPatch({pdfBranding:{logoURL:'https://example.invalid'}}));
  denied(()=>p.brandingPatch({plan:'enterprise'}));
  denied(()=>p.brandingPatch({primaryColor:'red'}));
  assert.deepEqual(p.brandingPatch({footerText:''}),{'pdfBranding.footerText':''});
});
test('PDF and image destinations validate signature and size',()=>{
  const fixture={name:'test.pdf',requestId:'attempt_1',kind:'constancia',contentBase64:Buffer.from('%PDF-1.4\nfixture').toString('base64')};
  assert.equal(p.upload(fixture).mime,'application/pdf');
  denied(()=>p.upload({...fixture,kind:'profile_photo'}));
  denied(()=>p.upload({...fixture,contentBase64:'not base64'}));
  denied(()=>p.upload({...fixture,contentBase64:Buffer.alloc(8*1024*1024+1).toString('base64')}));
  denied(()=>p.upload({...fixture,path:'org_b/file.pdf'}));
});
test('projections do not return secrets or arbitrary nested payload',()=>{
  const output=p.project({name:'A',secret:'x',items:[{name:'test',price:20,api_key:'private',organizationId:'org_b'}]},['name','items']);
  assert.deepEqual(output,{name:'A',items:[{name:'test',price:20}]});
});
test('a public request hash is not the connection credential',()=>{
  const secret='a'.repeat(43); assert.equal(p.secretId(secret),p.hash(secret));
  denied(()=>p.secretId(p.hash(secret)));
  denied(()=>p.identifier('../org_b'));
});
test('profile completeness preserves the QRclima weights',()=>{
  assert.equal(profileCompleteness({}),0);
  assert.equal(profileCompleteness({city:'A',photoURL:'x'}),10);
  assert.equal(profileCompleteness({alias:'test',city:'A',experienceYears:1,termsAcceptedAt:1,privacyAcceptedAt:1,
    baseLat:1,baseLng:1,signature:'x',preferredNavigationApp:'maps',photoURL:'x',stats:{servicesCount:1,qrsActive:1,sosSolved:1,trainingCompleted:1},
    achievements:{firstClient:true,firstAgenda:true,firstLabelsPdf:true}}),100);
});
