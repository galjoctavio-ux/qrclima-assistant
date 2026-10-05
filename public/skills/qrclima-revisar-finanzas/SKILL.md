---
name: qrclima-revisar-finanzas
description: Revisa ventas, cobros, deudas, gastos y vínculos financieros de QRclima mediante lecturas autorizadas. Úsala para explicar registros o proponer correcciones; no captura pagos, borra movimientos ni emite CFDI.
---

# Revisar registros financieros

Lee el [contrato de ejecución](../../references/runtime.md), perfil y organización seleccionados. Esta capacidad es de lectura. Comprueba el acceso actual antes de consultar datos comerciales.

Consulta el caso o periodo solicitado y conserva las referencias de los registros. Distingue venta, ingreso cobrado, deuda, egreso, costo y utilidad. Una cotización o factura no demuestra cobro ni recepción física.

Relaciona movimientos por sus IDs de origen, no solo por importe o nombre. No sumes como dos ingresos el cobro y el `amountPaid` de su venta. Diferencia fecha de operación, fecha de pago y fecha de captura.

Un costo desconocido no es cero. Si faltan materiales, mano de obra u otros costos, presenta la utilidad como provisional. Separa resultado de movimientos, margen de ventas y saldo bancario; no afirmes deducciones o beneficios fiscales sin evidencia suficiente.

Entrega hallazgos comprobados, inferencias identificadas, datos faltantes y corrección propuesta con el registro afectado. No ejecuta transferencias, cobros, eliminaciones, emisión fiscal ni solicitudes a terceros. Para una venta nueva, usa el chat y la skill de ventas bajo su alcance.

Consulta [adaptadores](../../references/adapters.md) si falta una lectura y conserva referencias según el [contrato de operación](../../schemas/operation.schema.json).
