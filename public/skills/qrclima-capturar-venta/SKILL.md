---
name: qrclima-capturar-venta
description: Prepara una venta de servicios en QRclima y permite registrarla por el portal cuando el modo y la instrucción del usuario lo autoricen. Distingue venta, cobro inicial y saldo; no emite facturas ni realiza pagos.
---

# Capturar venta de servicios

Lee el [contrato de ejecución](../../references/runtime.md), perfil y organización seleccionados. La primera versión usa clientes existentes y partidas de servicios; inventario y operaciones fiscales requieren un procedimiento adicional que este paquete no implementa.

Resuelve el cliente por registro, no solo nombre. Comprueba organización, sesión y permisos actuales. Consulta ventas existentes y vínculos del caso para detectar un registro previo antes de crear otro.

Prepara descripción, cantidad, precio, fecha de venta, importe realmente cobrado, método y fecha del cobro y cuenta receptora cuando aplique. Si el usuario no indica lo cobrado, pregunta: una venta no prueba pago y el formulario puede tomar un monto vacío como pago completo. No supongas cero ni el total.

Calcula las partidas y muestra el total, cobro y saldo. Los valores expresos prevalecen sobre estimaciones; QRclima vuelve a validarlos al guardar. No inventes costos, impuestos, referencias de pago, cuentas o comprobantes. Conserva fecha económica y fecha de captura separadas.

En `draft_only`, entrega el borrador y faltantes. En `confirm_each`, prepara la operación concreta y guarda por la interfaz cuando exista autorización suficiente en la sesión. No vuelvas a pedir aprobación de lo ya autorizado; resuelve únicamente incertidumbres materiales.

Después de guardar, relee venta, ingreso inicial y deuda cuando corresponda; comprueba cliente, conceptos, fechas, cobro y saldo. Conserva ID del registro y el recibo de intento. Ante error posterior al guardado, usa `outcome_unknown` y consulta antes de repetir. No corrijas importes ya cobrados o facturados desde una ruta alternativa.

Entrega estado, enlace o folio verificable y pendientes. Sigue [adaptadores](../../references/adapters.md) y el [contrato de operación](../../schemas/operation.schema.json).
