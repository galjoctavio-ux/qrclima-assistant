# Reconocimiento mínimo después de conectar

Forma parte del mismo caso de inicio activado por «inicio» o «inicia». Después de verificar lectura y escritura para el alcance elegido según [connection-acceptance.md](connection-acceptance.md), continúa con esta etapa en el mismo chat. La autorización que deba completar el usuario no crea un caso nuevo. No exijas otra petición para recuperar los datos básicos ni para comprobar la presencia de información dentro de los permisos concedidos.

Si faltan conexión, organización o evidencia de escritura, conserva la etapa como pendiente. Una lectura disponible por el portal puede aportar evidencia parcial, pero no permite afirmar que se cumplió la condición del conector.

## 1. Recuperar los datos básicos de la cuenta

Obtén el nombre del perfil, la referencia de cuenta, el UID, la organización elegida, su nombre, rol y plan cuando la fuente autorizada los exponga. Recupera otros campos básicos visibles del perfil o empresa solo si son necesarios para completar la configuración. Reutiliza lo comprobado antes de preguntar; un campo faltante permanece desconocido con su motivo.

`status` ya incorpora UID y datos de organización mediante el cliente actual. La asignación automática del nombre y de otros campos del perfil debe usar los campos realmente devueltos y documentados por el servidor; no inventes claves. Si la API no expone un dato, consulta el perfil por el portal disponible y registra esa fuente, o deja el dato pendiente. No extraigas secretos, configuración administrativa ni todos los datos del negocio bajo la expresión «información de la cuenta».

Guarda los datos básicos en el perfil privado con fuente, fecha y estado mediante `profile_store.py` y su revisión vigente. Estos campos no pertenecen a las instrucciones públicas.

## 2. Comprobar presencia y lectura por categoría

Comprueba solo las categorías soportadas y autorizadas para la organización elegida. En el cliente actual: clientes, conceptos normales, conceptos Pro, cotizaciones normales, cotizaciones Pro, citas, ventas y documentos del conector. Categorías ajenas al plan o al permiso quedan como no aplicables o inaccesibles según la evidencia; no intentes ampliar el acceso.

Realiza una consulta limitada a **un registro por categoría**, sin cursor ni recorrido de páginas. Un resumen fiable del servidor que ya acredite presencia y lectura con ese alcance puede evitar la consulta repetida. Reutiliza una lectura hecha durante la comprobación de conexión cuando corresponda a la misma cuenta, organización, categoría y caso de inicio.

El cliente existente permite, por ejemplo:

```text
python .agents/scripts/connector.py --root .qrclima read concepts --limit 1
python .agents/scripts/connector.py --root .qrclima read pro_concepts --limit 1
python .agents/scripts/connector.py --root .qrclima read quotes --limit 1
python .agents/scripts/connector.py --root .qrclima read pro_quotes --limit 1
```

Esos comandos devuelven una muestra limitada; el agente resume el resultado y evita imprimir datos comerciales innecesarios. Los nombres son categorías de la API autorizada, no autorización para enumerar colecciones arbitrarias de Firestore. Si solo existe la vía por portal, comprueba una muestra visible mínima y comunica el alcance de esa pantalla; no la presentes como acceso por conector.

| Resultado | Qué permite afirmar |
|---|---|
| Con datos y lectura comprobada | Se pudo leer al menos un registro dentro del alcance consultado |
| Sin resultados en el alcance | La consulta terminó correctamente sin registros; no demuestra por sí sola que una colección física no exista |
| Vacía en el alcance completo autorizado | La fuente acredita expresamente una consulta de todo ese alcance sin filtros y sin resultados; no implica ausencia de datos en otras organizaciones |
| Sin permiso | No se pudo comprobar presencia por falta de acceso |
| No soportada o no aplicable | La herramienta o el plan no ofrece esa categoría, según la evidencia consultada |
| Error o sin comprobar | No hay evidencia suficiente; conserva causa y pendiente |

Una muestra legible no acredita que todos los documentos de una categoría puedan leerse, ni concede escritura en esa categoría. Registrar una lista vacía con éxito acredita una consulta válida; una denegación no es una lista vacía. No inventes totales a partir de la muestra.

## 3. Guardar un resumen y continuar

Conserva un resumen privado del inicio ligado a cuenta, organización y fecha: campos básicos recuperados, resultado por categoría, límite utilizado, fuente, alcance o filtros, lectura comprobada y faltantes. Para justificar la presencia basta una referencia al registro leído; no archives la muestra comercial completa ni generes un índice del catálogo en esta etapa.

No uses `sync`, sigas cursores, descargues PDFs, generes documentos o recorras partidas por defecto. La [sincronización ampliada](synchronization.md) se realiza cuando el usuario la solicite o cuando una tarea concreta necesite sus registros, con el alcance mínimo correspondiente.

Termina con un resultado breve: identidad recuperada, categorías con datos y legibles, categorías sin resultados y límites o bloqueos. Pregunta solo por los faltantes que afecten al siguiente paso. No vuelvas a pedir el nombre que ya se obtuvo.

## Aceptación antes de 1.0.0

En una cuenta ficticia con muchas cotizaciones, el inicio obtiene datos básicos y comprueba categorías con un máximo de un registro por consulta, sin paginación ni descargas. En una cuenta sin registros distingue consulta vacía, permiso denegado y error. Comprueba variantes normales y Pro cuando proceda, preserva la organización seleccionada y continúa sin una segunda orden de reconocimiento. La prueba empieza después de acreditar lectura y escritura de la etapa de conexión.

Este procedimiento es una corrección local de instrucciones. La automatización completa, los campos de perfil del servidor y las pruebas reales de integración siguen sujetos a [PENDIENTES-1.0.0.md](../PENDIENTES-1.0.0.md).
