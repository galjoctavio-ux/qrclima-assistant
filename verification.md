# Verificación del piloto

## Revisión 0.4.1

Revisión del 5 de octubre de 2026, con datos ficticios y una carpeta extraída del ZIP público.

- Python: 51 casos, 50 correctos y uno omitido por el permiso de Windows para crear enlaces simbólicos.
- Control de publicación: 81 archivos de fuentes públicas y 50 archivos de la carpeta distribuida; referencias internas resueltas.
- ZIP workspace 0.4.1: integridad correcta, criterios de conexión, reconocimiento mínimo y registro de pendientes de 1.0.0 incluidos.
- Perfil ficticio creado mediante el script extraído: nombre, UID, organizaciones y preferencias vacíos; los nuevos parámetros de papeles comienzan en estado desconocido.
- Inspección del ZIP: sin perfiles, sesiones, contexto comercial, recibos privados, servidor ni integración del portal. Se comprobó que no contiene los datos de identidad observados durante el ensayo privado.

Las correcciones de esta versión son procedimientos y valores iniciales del perfil. No se ejecutaron operaciones con cuentas reales ni se activó el conector en QRclima. La comprobación del índice e historial se ejecuta antes del commit; CI vuelve a comprobarla al subir.

## Evidencia de 0.4.0

Revisión del 5 de octubre de 2026. El conector está implementado y probado localmente; su activación y recorrido con cuentas reales del portal permanecen pendientes.

## Conector 0.4.0

- Python: 51 casos, 50 correctos y 1 omitido en Windows por permiso de enlaces simbólicos. Incluye cifrado DPAPI real con una credencial ficticia, enlace de autorización sin secreto, preservación del perfil e impedimento de mezclar cuentas.
- Servidor: 16 tests correctos de política y HTTP: identidad verificada por Firebase, revocación comprobada, CORS limitado, flag deshabilitado, whitelist de campos, permisos y límites de archivos.
- Firestore/Auth/Storage reales en emuladores: 19 escenarios correctos con proyecto demo y reglas que niegan acceso directo. Incluyen organizaciones A/B, escrituras y relectura, documento privado, reintento, campos protegidos, cuenta desactivada, retirada de membresía, cambio de organización, bloqueo de eliminación, contactos cruzados, revocación durante subida y presupuesto por organización.
- Integración del portal: TypeScript y build de Next.js correctos en checkout aislado del portal. El build conserva avisos de hooks y Browserslist presentes en otros archivos; no se presenta como una limpieza de esos módulos.
- Paquete: nueve procedimientos comunes y nueve entradas de Claude; el cliente no incluye SDK administrativo, servidor ni datos personales. El control de fuentes, índice e historial y el ZIP se revisan antes de publicar.

No se han certificado login, consentimiento, documento y revocación con cuentas reales en producción ni compatibilidad operativa en todos los hosts. Una caída entre Storage y Firestore puede requerir conciliación de un intento reservado; no se presenta como recuperación automática completa ni versión 1.

## Evidencia anterior, versión 0.3.0

Revisión local del 5 de octubre de 2026, con datos ficticios y directorios aislados.

## Comprobado localmente

- `python -m unittest discover -s tests -q`: 44 casos, 43 correctos y 1 omitido en Windows por falta de permiso para crear un enlace simbólico real.
- Aislamiento de perfiles y organizaciones, revisiones concurrentes, escrituras completas, hechos declarados frente a verificados, modos de operación separados y resultados inciertos.
- Contexto con fuente, cobertura parcial, identidad, organización, paginación, revisión y actualización por fecha.
- Preferencias inicialmente vacías, migración compatible de perfiles anteriores, alcance y duplicados, conservación de datos y ausencia de permisos adicionales.
- Propuestas privadas y exportaciones idénticas antes y después de personalizar un perfil. Otro usuario mantiene los espacios vacíos.
- Control del índice lee el contenido preparado para Git, incluso si luego se limpió la copia de trabajo. El control de historial detecta perfiles borrados del commit actual.
- ZIP con integridad, referencias internas resueltas, licencia y 43 archivos públicos: 8 procedimientos comunes y 8 entradas de Claude que enlazan a ellos, más contratos, recursos e instrucciones.
- Proyecto generado en una ruta con espacios y CLI ejecutado como proceso separado; los datos nacen en `.qrclima/` fuera de las skills. Los helpers solo necesitan la biblioteca estándar de Python.

Los validadores comprueban contratos locales y patrones conocidos de secretos, no la autenticidad de una sesión ni anonimato semántico. Una marca de estado en un archivo no prueba que una operación comercial o una prueba real se haya ejecutado.

## Pendiente de evaluación real

Descubrimiento de las skills en cada cliente, herramientas de navegador, primer uso con una cuenta ajena al piloto, entrevista, importación completa o parcial observada y registro real de venta y cita con verificación posterior. El control desde teléfono y los hosts con otros proveedores también necesitan pruebas.

Los adaptadores se basan en documentación oficial de los clientes. Su existencia no certifica que cualquier modelo o chat pueda operar QRclima. El ZIP no instala un proveedor, conexión de navegador, VM, Firebase ni WhatsApp.

La guía visual ofrece el mensaje inicial y explica las capacidades necesarias. La verificación local de interfaz no prueba conexión comercial. Usa los [casos de aceptación](acceptance.md) y [criterios de versión 1](docs/VERSION-1.md) antes de anunciar estabilidad.
