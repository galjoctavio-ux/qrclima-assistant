# Tu asistente de QRclima

Empieza con **una carpeta y un chat**. La configuración, las consultas, ventas y agenda usan el mismo perfil. Los chats especializados son opcionales.

## Primer uso

1. Descomprime el ZIP en la ubicación que prefieras. Puedes cambiar el nombre de la carpeta.
2. Abre [EMPIEZA-AQUI.html](EMPIEZA-AQUI.html) para ver la guía visual.
3. Abre esta carpeta como proyecto en tu agente. Para Codex, agrégala como proyecto local y abre un chat asociado. Para Claude Code, Gemini CLI, Kimi o un host con DeepSeek, consulta [COMPATIBILIDAD.md](COMPATIBILIDAD.md).
4. Envía el mensaje siguiente. El asistente comprueba las herramientas, prepara el perfil y te ayuda a abrir tu sesión de QRclima.

> Inicia.

El agente comprobará Python y abrirá la autorización de QRclima. Inicia sesión, compara el código, elige tu organización y habilita los permisos que necesites. Vuelve al chat y escribe «continúa». La herramienta permite consultar tus datos y, con los permisos elegidos y una petición concreta, actualizar perfil, foto, logo o guardar una constancia privada. Consulta `.agents/references/connector.md`.

Si QRclima todavía no ha habilitado esta integración, el agente te lo dirá y utilizará el portal disponible. La carpeta no puede activar el servidor del proveedor. Una VM se pregunta únicamente para servicios externos que realmente la necesiten.

## Conectar el navegador

En Codex, la sesión puede estar en el navegador integrado, mencionado como `@Browser`, o en un navegador compatible. Para Chrome/Edge, revisa **Configuración → Computer Use/Uso del ordenador**, instala el plugin y la extensión que pida la aplicación y selecciona el navegador en el menú `@` del chat. En otro cliente conecta su propio controlador de navegador siguiendo su documentación. Inicia sesión en QRclima en ese perfil. Los nombres de controles y disponibilidad varían por versión o cuenta.

El asistente utiliza las herramientas reales que tenga el chat. Una carpeta no las instala por sí sola. Para la vía por navegador no necesitas Firebase CLI ni una llave administrativa. El agente comprobará si hay Python 3.10 o posterior disponible para los archivos locales y te indicará una limitación concreta si falta.

## Continuar con naturalidad

- «Prepara una venta para este cliente; vendí dos servicios y cobré este importe».
- «Ayúdame a registrar esta cita mañana; este es el cliente y este es el técnico».
- «Busca al cliente con teléfono terminado en 1234 y revisa su cita».
- «Actualiza mis conceptos y dime qué información sigue pendiente».

La información del negocio se consulta con tu sesión y sus permisos. Citas, conceptos y documentos pueden quedar parcialmente indexados si hay paginación, volumen o restricciones. Una operación real vuelve a comprobar el estado en QRclima. WhatsApp necesita una conexión propia; consultar un teléfono en QRclima no da acceso a sus mensajes.

## Lo que se guarda

```text
esta-carpeta/
  AGENTS.md                    instrucciones para el asistente
  EMPIEZA-AQUI.html             guía visual
  .agents/skills/               procedimientos por tarea
  .agents/references/           conexiones, entrevista y consultas
  .agents/scripts/              administradores locales
  .qrclima/                    se crea al configurar; tus datos privados
    profiles/principal/
      profile.json
      journal.jsonl
      context/                 registros observados por organización
      receipts/                evidencias de operaciones
```

La carpeta privada usa archivos locales sin cifrado añadido. Comparte el ZIP público original cuando quieras recomendar el asistente. Para actualizar instrucciones conserva `.qrclima/`.

## Aprender sin mezclar usuarios

Di «guarda esto como preferencia personal» o «esto es una mejora global del asistente». El agente clasifica y justifica el alcance mediante `qrclima-mejorar-asistente`. Una preferencia se guarda en `preferences` del perfil, con fuente y organización cuando corresponda. Las mejoras quedan registradas en `improvement_proposals`; la parte general puede llevarse al repositorio con datos ficticios. No se publica ni sincroniza automáticamente.

Hay espacios vacíos para estilo de respuesta, navegador, nombres de documentos, duración de citas y pie de cotizaciones. Puedes añadir otros. Un perfil nuevo no hereda valores de otro usuario. Una personalización no concede permisos de operación. Consulta el procedimiento en `.agents/references/improvements.md`.

## Comprobación del primer uso

El asistente debe informarte de la ruta del perfil, cuenta/organización comprobadas, qué pudo consultar y qué falta. La versión 0.4.0 es un piloto: scripts, adaptadores y empaquetado se prueban localmente; herramientas y operaciones reales se verifican en tu instalación. El kit no incluye suscripciones ni créditos del proveedor. Su uso y modificación se permiten bajo licencia MIT, incluida en la descarga.

Documentación oficial: [skills locales](https://learn.chatgpt.com/docs/build-skills), [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) y [conexión del navegador](https://learn.chatgpt.com/docs/chrome-extension).
