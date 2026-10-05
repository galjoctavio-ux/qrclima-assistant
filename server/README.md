# Servidor de QRclima para el asistente

Este componente lo opera QRclima, no cada usuario que descarga la carpeta. Usa Firebase Admin únicamente en el servidor. El cliente público conserva una credencial revocable de una organización; esa credencial no es un token administrativo ni un token válido para acceder directamente a Firestore.

`qrclimaAssistantAPI` pertenece a la codebase independiente `assistant`. La configuración no contiene un proyecto predeterminado ni despliega las reglas de QRclima. Desplegar solo esta función evita empaquetar otras funciones con cambios pendientes. La función arranca deshabilitada si no se configura expresamente.

## Contrato

El cliente genera 32 bytes aleatorios y conserva el secreto local. Su huella SHA-256 es la solicitud pública del navegador. El navegador verifica la cuenta Firebase e invita a revisar organización y permisos; el backend crea la concesión ligada a los documentos actuales del usuario y empresa. Saber la huella no permite usar la conexión. El enlace no contiene el secreto y no se intercambia el token Firebase con el agente.

Cada petición valida estado Auth, usuario activo, organización activa seleccionada, propiedad real o membresía admin, plan Pro Plus/Enterprise, caducidad y revocación. La eliminación en curso bloquea operaciones. Un cambio de organización, desactivación o retirada de membresía invalida la conexión. Los roles técnicos permanecen fuera del piloto, igual que en el portal administrativo actual.

Las consultas seleccionan colecciones y campos permitidos y siempre filtran `organizationId` derivado de la concesión. El cliente no puede aportar UID, organización, colección o ruta arbitrarios. Contactos privados de clientes se incorporan solo tras comprobar organización e ID. No se exponen secretos fiscales, claves, tokens ni colecciones administrativas.

Las escrituras de perfil/marca tienen whitelist, revisión exacta e intento idempotente. Se conserva la completitud del perfil con los pesos de QRclima; sus triggers actuales mantienen las proyecciones públicas. Los permisos Pro Plus excluyen el flujo de bonificación del perfil gratuito. No se duplican lógica de ventas, citas, deuda, stock o CFDI.

Fotos y logos van a los namespaces de QRclima y Firestore recibe su URL. El logo usa un objeto único dentro de `orgs/{orgId}` para no sobrescribir otro intento; actualiza `pdfBranding.logoURL`. Las constancias van a `assistant_private_documents/{orgId}/{id}.pdf` y metadata `assistant_documents/{id}`; no contienen token público de descarga. El acceso es por este endpoint con comprobación de pertenencia. Antes de activar, verifica que no haya una regla o política IAM pública que abra ese namespace.

Las subidas reservan un intento y un objeto único; revalidan el permiso al finalizar. Ante un conflicto conocido se elimina solo la generación creada por ese intento. Un corte entre Storage y Firestore deja el intento pendiente: se rechaza repetirlo y requiere conciliación administrativa. Esta recuperación y los tests reales del portal son puertas pendientes para versión 1.

## Verificar

Node 22 y Java 21 para el mantenedor; Python y navegador bastan en el cliente.

```sh
npm ci --ignore-scripts
npm test
firebase --config test/emulator-config.json emulators:exec --only firestore,auth,storage --project demo-qrclima-assistant "node test/emulator.cjs"
```

El harness exige el proyecto demo y hosts de emulador en loopback. Sus reglas niegan acceso directo y los casos usan exclusivamente datos ficticios. El archivo de reglas del harness no debe desplegarse a un proyecto real. La CLI requiere Java 21; no cambies la instalación global de Java para una prueba si puedes usar un runtime local.

## Activación por el operador

1. Integra [la pantalla de autorización](../integration/README.md), comprueba login y permisos en un entorno de prueba y revisa el diff.
2. Configura privadamente `QRCLIMA_ASSISTANT_PORTAL_ORIGIN` con el origen HTTPS exacto del portal, `QRCLIMA_ASSISTANT_BUCKET` con su bucket y `QRCLIMA_ASSISTANT_ENABLED=true` cuando corresponda activar. Guarda `.env.<project-id>` fuera del repositorio público; no copies credenciales de servicio al cliente.
3. Copia esta codebase revisada a una carpeta privada de despliegue y usa `firebase deploy --config firebase.json --project <proyecto-real-verificado> --only functions:assistant:qrclimaAssistantAPI`. No uses el proyecto demo para producción ni despliegues todas las codebases.
4. Configura en el portal la URL devuelta por el despliegue y el flag de activación. Verifica CORS y que el cliente descubra únicamente ese endpoint por `/assistant/connector-config`.
5. Antes de abrirlo al público, prueba una cuenta real distinta y dos organizaciones, un cambio autorizado y relectura, documento privado, revocación y pérdida de membresía. Las pruebas de emuladores no sustituyen ese recorrido.

Configura TTL para `assistant_connections.deleteAfter`, `assistant_rate_limits.expiresAt` y `assistant_upload_quotas.deleteAfter` para retirar metadatos vencidos. Conserva recibos según el criterio operativo de QRclima. La función limita conexiones activas y rechaza más de 100 concesiones históricas sin depuración; no ignora ese límite para dar acceso.

Para retirar el piloto, desactiva el flag del portal y del servidor y revoca concesiones. No borres documentos ni fotos de los usuarios para desactivar una herramienta. Registra la versión, entorno y evidencias de la activación.
