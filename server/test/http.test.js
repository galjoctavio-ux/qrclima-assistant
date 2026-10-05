'use strict';
const {test}=require('node:test'), assert=require('node:assert/strict');
const {createHttpHandler}=require('../http');
const {BridgeError}=require('../policy');
async function invoke(options={},overrides={}) {
  const calls=[];
  const bridge={rate:async()=>{},browser:async(...args)=>{calls.push(args);return{ok:true};},connector:async()=>({ok:true})};
  const handler=createHttpHandler({enabled:true,origin:'https://portal.example',bridge,verifyIdToken:async()=>({uid:'signed_user',auth_time:1}),...options});
  const req={headers:{origin:'https://portal.example'},method:'POST',rawBody:Buffer.from('{}'),ip:'127.0.0.1',body:{action:'approve'},
    is:()=>true,get:()=>['Bearer','synthetic-token'].join(' '),...overrides};
  const result={headers:{}};const res={set:(key,val)=>{result.headers[key]=val;},status:code=>{result.status=code;return res;},json:value=>{result.body=value;},end:()=>{}};
  await handler(req,res); return{result,calls};
}
test('disabled service fails before authentication or data access',async()=>{
  const {result,calls}=await invoke({enabled:false});assert.equal(result.status,503);assert.equal(calls.length,0);
});
test('untrusted Origin rejected, CORS is not wildcard',async()=>{
  const {result,calls}=await invoke({}, {headers:{origin:'https://untrusted.example'}});assert.equal(result.status,403);assert.equal(result.headers['Access-Control-Allow-Origin'],undefined);assert.equal(calls.length,0);
});
test('approval identity comes from verified ID token and checks revocation',async()=>{
  let checked;
  const {result,calls}=await invoke({verifyIdToken:async(token,revoked)=>{checked=revoked;return{uid:'signed_user',auth_time:100};}});
  assert.equal(checked,true);assert.equal(calls[0][0],'signed_user');assert.equal(result.status,200);assert.equal(result.headers['Cache-Control'],'no-store');
});
test('invalid or revoked Firebase token cannot approve',async()=>{
  const {result,calls}=await invoke({verifyIdToken:async()=>{throw Error('token secret that must not print');}});assert.equal(result.status,401);assert.equal(calls.length,0);assert.ok(!JSON.stringify(result).includes('token secret'));
});
test('missing credential and oversized body rejected',async()=>{
  assert.equal((await invoke({}, {get:()=>''})).result.status,401);
  assert.equal((await invoke({}, {rawBody:Buffer.alloc(12*1024*1024+1)})).result.status,413);
});
test('connection token is routed to scoped tools, not Firebase admin identity',async()=>{
  let credential;
  const bridge={rate:async()=>{},connector:async(key)=>{credential=key;throw new BridgeError('permission_denied','denied',403);}};
  const {result}=await invoke({bridge}, {body:{action:'read',category:'clients'}});assert.equal(credential,'synthetic-token');assert.equal(result.status,403);
});
