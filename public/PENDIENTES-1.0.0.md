# Pendientes para publicar la versión 1.0.0

Actualizado: 5 de octubre de 2026. Estado: preparación; publicación bloqueada por falta de evidencia de conexión y operaciones completas.

Este documento recoge requisitos y criterios de aceptación. No certifica que estén implementados. Los procedimientos forman parte del piloto 0.4.1. La carpeta descargable de uso no incluye el servidor ni las herramientas de publicación; estas se conservan en el repositorio de desarrollo. Las pruebas reales pendientes deben completarse en ese entorno.

## Resultado que debe ofrecer el primer contacto

Al recibir «inicia», el asistente debe comprobar primero una conexión fiable a la cuenta y organización elegidas. Antes de declarar la configuración completa debe acreditar identidad, permisos, una lectura real y una escritura persistida dentro del alcance ofrecido. Ver una sesión abierta o guardar el perfil local solo acredita esa parte.

El resultado debe distinguir conexión verificada, configuración parcial y bloqueo. Consulta el [criterio de conexión](references/connection-acceptance.md). Después de acreditar lectura y escritura, «inicio» o «inicia» debe continuar en el mismo caso con el [reconocimiento mínimo](references/initial-discovery.md): recuperar nombre y datos básicos, y comprobar presencia y lectura de conceptos, cotizaciones y otras categorías autorizadas sin cargar el negocio completo. La entrevista posterior reutiliza esos datos; la importación ampliada depende de una petición o tarea concreta.

## Evidencia disponible y sus límites

| Aspecto | Evidencia | Conclusión permitida |
|---|---|---|
| Distribución | `VERSION.json` generado para el ZIP declara la versión del piloto | Es un piloto; no es 1.0.0 |
| Conector local | [connector.py](scripts/connector.py) implementa autorización, estado, lecturas y cambios limitados | Existe un cliente; esto no demuestra que el servidor esté habilitado |
| Escrituras del conector | `update profile|branding`; subida de foto, logo y constancia | Las escrituras comerciales no están contempladas por este cliente |
| Operaciones comerciales | Los procedimientos actuales usan el portal para ventas y citas; finanzas inicia en lectura | Cada operación necesita una prueba completa por la vía realmente soportada |
| Compatibilidad | `COMPATIBILIDAD.md` del ZIP declara validación con datos ficticios y emuladores | Esa declaración no certifica operaciones reales en todos los clientes |
| Primer uso observado | La integración informó que aún no estaba habilitada; había una sesión del portal | Configuración parcial; lectura y escritura por el conector sin verificar |

El último resultado es una observación del piloto, no una afirmación sobre todas las instalaciones ni una comprobación continua del servicio. Sus detalles quedan en el registro privado de mejoras.

## Trabajo priorizado

P0 bloquea una publicación que anuncie las capacidades afectadas. P1 debe resolverse antes de declarar una distribución pública mantenible. «Documentado» significa que existe el requisito, no que pasó su prueba.

| ID | Prioridad | Pendiente | Estado | Criterio para cerrarlo |
|---|---|---|---|---|
| CON-01 | P0 | Habilitar servidor y autorización del conector | Pendiente de implementación o activación en QRclima | Una instalación nueva autoriza la organización elegida; `status` devuelve identidad, rol y permisos concordantes |
| CON-02 | P0 | Comprobar lectura real y aislamiento por organización | Sin verificar por conector | Una consulta devuelve registros actuales con ID, organización y paginación; otra organización queda inaccesible |
| CON-03 | P0 | Definir e implementar las escrituras que promete 1.0.0 | Alcance comercial por decidir | Cada operación anunciada tiene un contrato autorizado, validaciones, ID de intento, persistencia y lectura posterior |
| CON-04 | P0 | Verificar escritura y recuperación ante respuesta incierta | Sin prueba completa | Una prueba autorizada persiste y se relee; repetir el mismo intento no duplica; un conflicto obliga a conciliar |
| CON-05 | P0 | Comprobar revocación, caducidad, cambio de cuenta y recuperación | Sin pruebas reales acreditadas en esta carpeta | El acceso revocado o de otra cuenta se rechaza; la reconexión conserva el perfil correcto sin mezclar organizaciones |
| INI-01 | P0 | Distinguir sesión, conexión y capacidad de operación durante el inicio | Corrección documental incorporada al kit | El asistente comunica alcance probado y faltantes; una integración deshabilitada nunca termina como configuración completa |
| INI-02 | P0 | Recuperar datos básicos y reconocer categorías en el mismo inicio | Procedimiento documentado; integración real sin verificar | Después de acreditar lectura y escritura, obtiene nombre e identidad disponibles y comprueba categorías autorizadas con hasta un registro por consulta; sin paginación, descarga completa ni segunda orden. Distingue datos legibles, consulta vacía, falta de permiso y error |
| QA-01 | P0 | Probar los flujos anunciados de principio a fin | Pendiente | Casos con datos ficticios en una organización de prueba: lectura, venta y cita si se ofrecen; recibo, relectura y efectos concordantes |
| REL-01 | P0 | Verificar que el paquete público excluye datos privados | Pendiente en las fuentes | Construcción con lista de archivos permitidos y `python tools/check_public.py`; inspección del ZIP y de una instalación limpia |
| CMP-01 | P1 | Delimitar clientes realmente soportados | Pendiente | Matriz con cliente, versión, herramientas y pruebas ejecutadas; compatibilidad restante presentada como pendiente |
| DOC-01 | P1 | Ofrecer diagnóstico y recuperación comprensibles | Criterios documentados | Pruebas de primer uso muestran faltantes concretos y pasos útiles sin solicitar secretos ni infraestructura administrativa |
| CFG-01 | P1 | Conservar preferencias y permitir distinguir el papel de quien desarrolla el sistema | Parámetros vacíos incorporados al generador del kit; falta prueba de actualización del paquete | Un perfil nuevo tiene valores vacíos; una actualización conserva el perfil existente sin heredar datos del piloto |

## Alcance y decisión de implementación

El requisito funcional es que el asistente pueda leer y registrar lo que el usuario le pide en QRclima. La vía recomendada es un conector del usuario con acciones concretas que use las validaciones del servidor y compruebe cuenta, organización, rol y permiso en cada llamada. El SDK administrativo y el acceso genérico a colecciones no son necesarios para cumplir ese requisito.

Hay que decidir qué operaciones comerciales incluirá 1.0.0. El cliente actual conserva ventas y citas en el portal y finanzas en lectura. Si 1.0.0 promete escritura comercial por el conector, necesita nuevos contratos y cliente; modificar una skill no crea esa capacidad. Si mantiene una vía por interfaz, deberá validar y anunciar esa dependencia con precisión.

Una escritura de diagnóstico prueba la persistencia del diagnóstico. No certifica por sí sola una venta, una cita ni todos los permisos comerciales. Cada operación anunciada requiere su propio caso completo de aceptación.

## Pruebas antes de publicar

1. Instalar el paquete público en una carpeta nueva con perfil vacío y un cliente soportado.
2. Autorizar una cuenta y organización de prueba; comprobar su identidad y permisos.
3. Leer registros ficticios, recorrer paginación y comprobar aislamiento respecto de otra organización.
4. Ejecutar las escrituras anunciadas con autorización del caso; conservar ID de intento y registro, leer lo persistido y comprobar sus efectos.
5. Simular pérdida de respuesta, repetición, conflicto, revocación y reconexión; comprobar que no aparecen duplicados ni mezclas de cuenta.
6. Repetir los flujos críticos en cada cliente anunciado y verificar el paquete público.

Para INI-02, usar cuentas ficticias con información abundante, sin registros y con permisos restringidos. Comprobar nombre recuperado, variantes normales y Pro cuando proceda, organización conservada, límite de un registro por categoría, ausencia de paginación y descargas, y continuación en el mismo caso. Verificar qué campos básicos expone realmente `status` y completar su contrato si faltan.

Registrar para cada prueba: fecha, versión del kit y del servidor, cliente, capacidad, entorno, pasos, resultado y evidencia privada. Los estados deben ser pendiente, ejecutada con fallo o aprobada con evidencia. La documentación de emuladores no sustituye las pruebas reales de integración.

## Siguiente paso

Resolver CON-01 en el proyecto de QRclima y concretar CON-03. Después ejecutar CON-02 y CON-04 en una organización de prueba. Mantener la publicación 1.0.0 pendiente hasta que estén acreditados los P0 del alcance anunciado.
