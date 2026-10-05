# Verificación del piloto 0.3.0

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
