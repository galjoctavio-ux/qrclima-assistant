# Criterios para versión 1

El objetivo es una carpeta que un usuario pueda configurar con su cuenta, conversar naturalmente y completar tareas básicas verificadas, manteniendo preferencias y datos privados separados del kit común. El piloto del mantenedor orienta el diseño; no demuestra que funcione para otra empresa.

Los requisitos detallados y prioridades se mantienen en [PENDIENTES-1.0.0.md](../public/PENDIENTES-1.0.0.md), incluido en la distribución. Las comprobaciones del primer contacto se definen en el [criterio de conexión](../public/references/connection-acceptance.md) y el [reconocimiento mínimo](../public/references/initial-discovery.md). Instrucciones incorporadas al kit no equivalen a integración real aprobada.

## Alcance inicial

- Una conversación con configuración progresiva, perfil y contexto por organización.
- Ventas sencillas de conceptos existentes, pago conocido y verificación del registro y sus vínculos.
- Consulta y registro de citas con disponibilidad, zona horaria y verificación posterior.
- Revisión financiera de lectura que distinga venta, cobro, deuda, gasto y coste.
- Preferencias opcionales vacías y proceso para promover mejoras comunes.

- Conexión propia revocable, perfil/marca y documentos privados; aislamiento de organizaciones probado en servidor.

## Puertas de salida

| Evidencia necesaria | Estado en 0.4.0 |
|---|---|
| Controles locales, empaquetado limpio y revisión del índice/historial | Implementados; resultados en verification.md |
| Primer uso en carpeta nueva y cuenta distinta, sin datos del piloto | Pendiente de prueba real |
| Lectura y escritura acreditadas antes de declarar completa la conexión | Criterio incorporado en 0.4.1; integración real pendiente |
| Nombre y datos básicos recuperados; presencia por categoría con hasta un registro, sin paginación o descargas y sin una segunda orden | Procedimiento incorporado en 0.4.1; ejecución real pendiente |
| Venta y cita reales en organización de prueba, con relectura | Pendiente |
| Cuenta sin permisos suficientes y cambio de organización | Pendiente de prueba real |
| Fallo de guardado, recuperación y ausencia de duplicados | Lógica local probada; portal pendiente |
| Preferencias de dos usuarios sin contaminación y actualización que las conserve | Aislamiento local probado; uso real pendiente |
| Cada cliente anunciado como operativo: versión, navegador, sesión y flujo probado | Pendiente; adaptadores documentados |
| Descarga pública con campos personales vacíos y guía revisada | Incluida en piloto público |

Registra fecha, versión del kit, cliente, alias de prueba, pasos, resultado y evidencia privada. Publica solo un resumen sin datos personales. No marques completado un caso por escribir una plantilla o porque haya pasado una prueba local.

La versión 1 puede certificar inicialmente un cliente y declarar los otros como compatibilidad de instrucciones en evaluación. Ser portátil no obliga a certificar simultáneamente todas las herramientas de navegador.

## Preparar la publicación

Congela alcance, ejecuta controles y casos reales, revisa fuentes públicas, construye una carpeta nueva y examina el ZIP. Cada nuevo perfil mantiene identidad, organización, rutas y preferencias desconocidas hasta que el usuario las aporte o se comprueben con su sesión.

El proceso excluye datos privados desde el origen. No limpia perfiles del mantenedor ni borra carpetas de uso. Si un dato privado entra en Git, se trata como una exposición: quitarlo del archivo actual no elimina su historial. Revisa y remedia antes de distribuir.

WhatsApp, facturación, inventario, escrituras comerciales por conector, VM y automatizaciones avanzadas quedan para versiones posteriores. No prometas ahorro de tokens, operación móvil o fiabilidad universal sin medirlos en el host concreto.
