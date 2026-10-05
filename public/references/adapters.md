# Adaptadores y capacidades disponibles

Este documento define interfaces de trabajo. No declara herramientas instaladas ni un servidor implementado. El agente descubre herramientas disponibles y sigue su documentación actual.

| Adaptador | Primera versión | Condición de uso |
|---|---|---|
| Navegador | Ruta prevista para QRclima | Controlador disponible, sesión propia, organización y permisos comprobados |
| Archivos locales | Administrador de perfiles implementado | Directorio privado seleccionado; no leer otras cuentas |
| Índice de contexto | Snapshots y búsqueda local implementados | Cuenta/organización concordantes, fuente y cobertura; el agente aporta lecturas reales |
| Control remoto móvil | Capacidad del runtime | Conexión y host realmente disponibles; no se deduce por tener teléfono |
| Lectura SDK | Contrato futuro | Herramienta autenticada por usuario y filtrada por organización; no incluir claves administrativas |
| Máquina virtual | Configuración opcional | Finalidad explícita y conexión individual autorizada; sin ejecutar una ruta como comando |
| WhatsApp | Fuera del piloto inicial | Adaptador, identidad, destinatarios y autorización de cada alcance probados aparte |
| Escritura SDK | Fuera del piloto inicial | Servicio de negocio que aplique permisos, reglas, transacciones y control de reintentos |

## Navegador

El agente carga documentación del controlador disponible, identifica la pestaña y lee el estado real. No supone nombres de herramientas ni copia selectores de otra instalación. Navega mediante controles observados, prepara los campos y verifica el resultado posterior.

Antes de una mutación se comprueba la cuenta, organización, rol/plan requerido y autorización del caso. Si una operación no existe o cambió la interfaz, se reporta la limitación. El paquete de usuario no modifica ni despliega QRclima.

## Contrato futuro para herramientas autenticadas

Una herramienta de consulta debe devolver `actor_uid`, `organization_id`, `observed_at`, resultados limitados y referencias de evidencia. El servidor deriva el actor de la sesión y verifica la membresía; no confía en un UID elegido por el modelo.

Una herramienta de escritura recibe una operación concreta y un `attempt_id` estable. Revalida acceso y datos, ejecuta conjuntamente sus efectos y devuelve el estado persistido. Los totales, cobros, deudas, stock y bloqueos se validan mediante la lógica compartida de QRclima.

No ofrecer una herramienta genérica para ejecutar JavaScript, consultar cualquier colección, escribir cualquier documento o reutilizar credenciales de otro usuario.
