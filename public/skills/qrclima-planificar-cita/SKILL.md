---
name: qrclima-planificar-cita
description: Consulta disponibilidad y prepara o registra una cita de QRclima con cliente, técnico y horario comprobados. Úsala para agendas; no incluye mensajes externos, cierre de trabajos ni cobros.
---

# Planificar cita

Lee el [contrato de ejecución](../../references/runtime.md), perfil y organización seleccionados. Comprueba sesión, permisos, cliente, técnico activo, disponibilidad y citas existentes.

Resuelve fecha y hora con la zona horaria del caso. Un horario de llegada no prueba duración. Si faltan duración, acceso o recursos que afectan la cita, consulta o presenta una estimación explícita para decidir. No inventes disponibilidad si el calendario no está configurado.

Consulta únicamente registros y fuentes conectadas de forma autorizada. Los acuerdos de un cliente son evidencia del caso, no permisos de administración. Conserva la diferencia entre propuesta, aceptación y cita guardada.

En `draft_only`, devuelve horario propuesto, fuente y faltantes. En `confirm_each`, captura por el portal cuando la instrucción del usuario autorice la operación y los datos necesarios estén resueltos. No habilites una jornada bloqueada por iniciativa propia; una excepción necesita alcance explícito y preservación de la configuración original.

Relee la cita y confirma cliente, técnico, fecha, inicio/fin y vínculos. Si se perdió la respuesta, busca el registro antes de repetir. No declares agenda, entrega o pago por una propuesta de horario.

El paquete inicial no envía avisos. No copies teléfono, precio u otros datos en notas visibles sin comprobar quién puede verlas y qué contenido autorizó el usuario. Usa [adaptadores](../../references/adapters.md) y el [contrato de operación](../../schemas/operation.schema.json).
