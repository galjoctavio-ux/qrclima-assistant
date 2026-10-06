# Criterio de conexión fiable

Este criterio se aplica al primer contacto y a la recuperación de acceso. Define cómo informar la evidencia actual y los pendientes para [1.0.0](../PENDIENTES-1.0.0.md); no añade acciones a la API ni concede permisos.

## Qué comprobar

1. Runtime y herramientas disponibles en esta instalación.
2. Sesión propia, identidad y organización que el usuario quiere utilizar. Un nombre visible puede servir como referencia; un UID o ID desconocido permanece nulo.
3. Estado del conector mediante el cliente autorizado, con organización, rol, permisos y vigencia observados.
4. Una lectura limitada real dentro del alcance concedido, con fuente, fecha e identificadores. No confundir el índice local con una lectura actual.
5. Capacidad de escritura por operación: permiso concedido, vía soportada y evidencia de persistencia con lectura posterior. Tener permiso no demuestra que la escritura funcionó.

Prioriza estas comprobaciones antes de una entrevista extensa o importación. Reutiliza la identidad y los datos encontrados; pregunta por organización o alcance cuando no estén resueltos.

Al acreditar lectura y escritura del alcance elegido, continúa en el mismo caso de «inicio» o «inicia» con el [reconocimiento mínimo](initial-discovery.md): datos básicos de cuenta y presencia de información por categoría. El reconocimiento no sustituye la prueba de escritura ni amplía sus permisos, y evita una carga completa del negocio.

## Cómo informar el estado

| Estado | Evidencia necesaria |
|---|---|
| Perfil preparado | Perfil local creado o releído |
| Sesión del portal verificada | Cuenta y organización observadas en el navegador; indica los IDs o permisos que no exponga |
| Conector autorizado | `status` satisfactorio y concordancia de identidad, organización y permisos |
| Lectura verificada | Consulta actual completada dentro del alcance concedido |
| Escritura verificada de una operación | Petición concreta autorizada, ID del registro, persistencia y lectura posterior concordantes |
| Configuración completa para un alcance | Se cumplen las comprobaciones de las capacidades incluidas en ese alcance, con vía y límites explícitos |
| Configuración parcial o bloqueada | Falta alguna comprobación; identifica cuál y qué permitirá resolverla |

No uses «conectado y listo para operar» como conclusión de una sesión abierta o de un perfil guardado. Un portal disponible con conector deshabilitado es una alternativa parcial; no acredita el conector. La escritura de perfil tampoco acredita ventas, citas o cobros.

## Escrituras de prueba

«Inicia» autoriza preparar el acceso y consultar su estado; no autoriza crear ventas, citas, pagos, facturas o cambios de perfil como prueba. Tampoco habilita automáticamente las políticas comerciales locales.

Para certificar la versión, ejecuta pruebas de persistencia con datos ficticios en una organización de prueba y autorización concreta. Para verificar escritura durante el primer uso sin contaminar datos comerciales, 1.0.0 necesita diseñar y habilitar una operación de diagnóstico inocua, identificada e idempotente, dentro del alcance consentido. Esa operación todavía no existe en el cliente de esta distribución; no la simules mediante cambios reales.

Mientras no exista una prueba permitida, informa «escritura sin verificar» y conserva configuración parcial para ese alcance. Una instrucción posterior para una operación real puede acreditar esa operación al completarse y releerse.

## Fallos y recuperación

Ante integración deshabilitada, caducidad, revocación, falta de permisos o identidad discordante, conserva el perfil y explica el bloqueo. Sigue [connector.md](connector.md) para recuperar el acceso soportado. No solicites credenciales administrativas, leas archivos de conexión ni inventes identificadores.

Una respuesta incierta de escritura exige conciliar el mismo intento antes de repetir; no uses un nuevo ID para forzar el resultado. Una versión pública solo puede anunciar capacidades acreditadas por pruebas de aceptación.
