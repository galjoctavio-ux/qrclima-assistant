'use strict';
const {BridgeError,fail} = require('./policy');
function createHttpHandler({enabled,origin,bridge,verifyIdToken}) {
  return async (req,res) => {
    res.set('Cache-Control','no-store'); res.set('X-Content-Type-Options','nosniff');
    if (req.headers.origin && req.headers.origin !== origin) { res.status(403).json({error:{code:'permission_denied',message:'Origen no permitido.'}}); return; }
    if (req.headers.origin === origin && origin) {
      res.set('Access-Control-Allow-Origin',origin); res.set('Vary','Origin');
      res.set('Access-Control-Allow-Headers','Authorization, Content-Type'); res.set('Access-Control-Allow-Methods','POST, OPTIONS');
    }
    if (req.method === 'OPTIONS') { res.status(204).end(); return; }
    try {
      if (!enabled) fail('unavailable','El conector está en preparación. Usa el portal mientras se habilita.',503);
      if (!origin || !/^https:\/\/[^/]+$/.test(origin)) fail('unavailable','La configuración del conector no está completa.',503);
      if (req.method !== 'POST' || !req.is('application/json')) fail('invalid_argument','Usa una solicitud JSON POST.',405);
      if (req.rawBody.length > 12*1024*1024) fail('invalid_argument','Solicitud demasiado grande.',413);
      const match = new RegExp('^' + ['Bearer','(\\S+)$'].join(' ')).exec(req.get('Authorization') || '');
      if (!match) fail('unauthenticated','Falta la conexión.',401);
      await bridge.rate('ip:' + req.ip,120,60000);
      let result;
      if (['preview','approve','connections','revoke'].includes(req.body?.action)) {
        let token;
        try { token = await verifyIdToken(match[1],true); }
        catch { fail('unauthenticated','Vuelve a iniciar sesión en QRclima.',401); }
        result = await bridge.browser(token.uid,token.auth_time,req.body);
      } else result = await bridge.connector(match[1],req.body);
      if (Buffer.byteLength(JSON.stringify(result)) > 12*1024*1024) fail('resource_exhausted','Reduce el tamaño de la página solicitada.',413);
      res.status(200).json({result});
    } catch (error) {
      const known = error instanceof BridgeError;
      if (!known) console.error('assistant_request_failed',{code:'internal'});
      res.status(known?error.status:500).json({error:{code:known?error.code:'internal',
        message:known?error.message:'No se completó la operación. Revisa su resultado antes de repetirla.'}});
    }
  };
}
module.exports={createHttpHandler};
