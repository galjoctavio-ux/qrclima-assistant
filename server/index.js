'use strict';
const admin = require('firebase-admin');
const {onRequest} = require('firebase-functions/v2/https');
const {createBridge} = require('./core');
const {createHttpHandler} = require('./http');
admin.initializeApp();
exports.qrclimaAssistantAPI = onRequest({region:'us-central1', timeoutSeconds:60, memory:'512MiB', maxInstances:3}, async (req,res) => {
  const enabled=process.env.QRCLIMA_ASSISTANT_ENABLED==='true' && !!process.env.QRCLIMA_ASSISTANT_BUCKET;
  const handler=createHttpHandler({enabled,origin:process.env.QRCLIMA_ASSISTANT_PORTAL_ORIGIN,
    bridge:enabled?createBridge({db:admin.firestore(),auth:admin.auth(),bucket:admin.storage().bucket(process.env.QRCLIMA_ASSISTANT_BUCKET)}):null,
    verifyIdToken:(token,revoked)=>admin.auth().verifyIdToken(token,revoked)});
  await handler(req,res);
});
