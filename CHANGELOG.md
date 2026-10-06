# Cambios

## 0.4.1 — criterios de conexión y reconocimiento mínimo

- «Inicio» e «inicia» comparten el mismo caso de configuración, con prioridad al acceso antes de una entrevista extensa.
- Se distingue sesión del portal, conector autorizado, lectura y escritura persistida por operación; las capacidades sin evidencia quedan pendientes.
- Después de acreditar la conexión, el procedimiento recupera datos básicos y comprueba presencia y lectura con hasta un registro por categoría autorizada, sin `sync`, paginación o descargas completas por defecto.
- Consultas vacías, falta de permisos, categorías no soportadas y errores tienen resultados distintos.
- Registro de pendientes de 1.0.0 incluido en el ZIP y mantenido por la skill de mejoras, con prioridades y aceptación.
- Parámetros opcionales `project-role` y `assistant-role` vacíos en perfiles nuevos; valores personales fuera de la distribución.
- Correcciones de procedimientos y empaquetado. La activación del conector y las pruebas reales de lectura/escritura siguen pendientes; no se modificó ni desplegó el servidor.

## 0.4.0 — conector propio en piloto

- «Inicia» prepara una conexión autorizada en navegador, ligada a una organización y permisos concretos.
- Cliente Python sin SDK administrativo, con credencial privada protegida y carga de contexto resumida.
- Servidor independiente con validación actual de cuenta, membresía, plan, revocación y caducidad.
- Lecturas acotadas y cambios de perfil/marca; foto y logo en Storage; constancias privadas con metadata en Firestore.
- Pantalla de autorización y revocación para integrar en QRclima, deshabilitada hasta activar el entorno.
- Tests de servidor, cliente, aislamiento y subidas con emuladores y datos ficticios. Ventas y citas conservan los flujos existentes.

## 0.3.0 — piloto público

- Entradas para Codex, Claude Code, Gemini CLI, Kimi Code CLI y lectura explícita para otros hosts, incluido DeepSeek.
- Ocho skills con fuente común y adaptadores de Claude generados como referencias.
- Preferencias privadas opcionales y vacías, con fuente y alcance por organización.
- Registro privado y clasificación de mejoras globales, personales, mixtas o pendientes de evidencia.
- Fuentes públicas aisladas del piloto, licencia MIT, contribuciones y criterios de versión 1.
- Control del índice y del historial de Git, y comprobaciones automáticas.

La compatibilidad operativa y los flujos reales del portal siguen pendientes de evaluación. Esta entrega no es la versión 1.

## 0.2.0 — piloto local

Una carpeta y una conversación, guía visual, siete skills, perfil y contexto por organización.

## 0.1.0 — esqueleto local

Procedimientos iniciales, contrato de perfil y administrador local sin conexión de red.
