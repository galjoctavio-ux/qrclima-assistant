# Herramienta propia de QRclima

El cliente descargable usa Python 3.10+ y HTTPS de la biblioteca estándar. No lleva Firebase Admin, llaves de servicio ni una llave de IA. El servidor de QRclima verifica la sesión Firebase del usuario al autorizar, concede una conexión limitada a su organización y vuelve a comprobar cuenta, membresía, rol, plan y revocación en cada operación.

## Uso desde la carpeta del asistente

```sh
python .agents/scripts/connector.py --root .qrclima inicia
python .agents/scripts/connector.py --root .qrclima status
python .agents/scripts/connector.py --root .qrclima sync --max-pages 3
python .agents/scripts/connector.py --root .qrclima read clients --limit 50
python .agents/scripts/connector.py --root .qrclima read appointments --limit 50
python .agents/scripts/connector.py --root .qrclima read documents
python .agents/scripts/connector.py --root .qrclima disconnect
```

El agente ejecuta estos comandos; el usuario puede escribir únicamente «inicia» y conversar. La autorización requiere entrar en el navegador, comprobar un código y elegir permisos. Al terminar vuelve al chat y escribe «continúa». El código y enlace no contienen la credencial.

El asistente también reconoce «inicio» como petición conversacional; el comando Python sigue siendo `inicia`. Después de acreditar lectura y escritura, aplica el [reconocimiento mínimo](initial-discovery.md) en el mismo caso. `read <categoría> --limit 1` permite comprobar una muestra; no uses `sync` como comprobación automática de existencia. El nombre y otros campos básicos deben proceder de la respuesta documentada del servidor o del perfil visible en el portal.

En Windows la conexión se cifra con DPAPI para el usuario del sistema. En macOS/Linux se guarda con permisos 0600, dentro de una carpeta 0700. `.qrclima/` queda fuera de Git y del ZIP. Esto no aísla el secreto frente a programas con acceso a la misma cuenta del sistema: el agente y el ordenador siguen siendo parte del entorno de confianza. No subas esa carpeta ni la incluyas al pedir soporte.

La conexión caduca a los 30 días. Puede revocarse en la página de autorización o con `disconnect`. Cambiar de organización requiere una nueva conexión. `cancel-pending` permite descartar una solicitud que no esté activa, tras comprobarlo con el servidor; no borra datos comerciales.

## Acciones del piloto

| Permiso | Acciones |
|---|---|
| Lectura de negocio | Perfil y empresa; clientes; servicios/citas; conceptos normales y Pro; cotizaciones normales y Pro; ventas; metadatos y descarga de documentos creados por el conector |
| Escritura de perfil | Nombre propio, empresa personal, ciudad y teléfono; foto de perfil |
| Escritura de marca, solo propietario | Nombre de organización, pie de PDF, color y logo; preserva el resto de ajustes |
| Documentos privados | Subir una constancia PDF y guardar su metadata ligada a la organización |

PNG/JPEG: perfil máximo 5 MiB y logo 2 MiB. PDF: constancia máximo 8 MiB. El servidor comprueba firma, destino y tamaño; no realiza una auditoría antivirus del documento. Fotos y logos tienen la misma visibilidad pública que sus equivalentes de QRclima. Las constancias van a un espacio privado, sin enlaces públicos de descarga.

Ejemplo de borrador privado para `update profile`:

```json
{"patch":{"fullName":"Nombre elegido"},"expectedRevision":"revision-obtenida-en-status","requestId":"intento-unico","confirmed":true}
```

Usa la revisión exacta devuelta por `status`. Los cambios fiscales, CSD, facturas, pagos, ventas, inventario, citas y mensajes conservan los servicios y procedimientos del portal. Una constancia subida no configura un emisor. Las consultas de citas muestran servicios de la organización, no certifican disponibilidad del técnico.

Hay límites de 100 registros por página, 60 solicitudes por minuto y 1000 diarias por conexión; además 20 archivos y 50 MiB diarios por organización. Se permiten hasta 10 conexiones activas por cuenta. Estos límites controlan uso del conector; los tokens de IA dependen del proveedor del usuario. El kit no incluye una suscripción de IA.

`sync` guarda un contexto observado con cobertura parcial, fuentes y fecha. Por defecto consulta hasta tres páginas por categoría y resume la carga; no imprime todos los registros al chat. Los PDFs históricos, facturas y adjuntos de otros módulos se consultan por el portal hasta integrar sus contratos. Antes de operar, relee el registro actual.

El conector necesita que QRclima publique y habilite su servidor y la pantalla de autorización. Una carpeta nueva no puede activar infraestructura del proveedor. Si `/assistant/connector-config` declara la herramienta deshabilitada, el cliente se detiene sin crear credenciales y utiliza el flujo del portal disponible.
