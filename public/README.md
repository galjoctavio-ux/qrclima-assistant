# Paquete de agentes de QRclima

Versión de piloto 0.3.0. El asistente reúne ocho skills para usar QRclima en una conversación y conservar contexto privado por organización. Cada usuario aporta su agente, cuenta de QRclima y herramientas para archivos y navegador. Los procedimientos son compartidos; herramientas y descubrimiento se comprueban en cada instalación.

## Empezar

El piloto necesita un entorno con lectura y escritura de archivos locales, Python 3.10 o posterior y un controlador de navegador compatible para las operaciones del portal. El administrador de perfiles usa solo la biblioteca estándar. Un chat que únicamente permite texto no adquiere esas herramientas al importar una skill. El uso desde el teléfono requiere un host o runtime conectado, comprobado aparte.

Empieza con `qrclima-asistente` o una petición natural de configurar QRclima. El agente lee el perfil, configura la sesión y aplica las skills pertinentes. La skill de sincronización consulta empresa, clientes, conceptos, citas, cotizaciones y documentos por etapas, sin cambiar operaciones comerciales. Sigue la [guía de carga inicial](references/synchronization.md).

Las plantillas de [configuración](agents/configuracion.md), [ventas](agents/ventas.md), [agenda](agents/agenda.md) y [finanzas](agents/finanzas.md) son opcionales. Todos los chats relacionados utilizan el mismo perfil seleccionado.

## Límites de esta versión

Ventas y agenda comienzan con borradores. La revisión financiera es de lectura. SDK de escritura, mensajes externos, emisión fiscal y modificaciones de la aplicación están fuera del paquete inicial. El navegador y cada operación real deben comprobarse con una cuenta de prueba antes de ofrecer el flujo a usuarios.

Los archivos en `schemas/` y `templates/` documentan perfil, casos y snapshots. `scripts/profile_store.py` administra preferencias; `scripts/context_store.py` guarda y busca registros observados por organización. Son administradores locales; la lectura del portal la realiza una herramienta de navegador del agente. Las rutas siguen [el contrato de ejecución](references/runtime.md).

`qrclima-mejorar-asistente` separa mejoras generales de valores privados. El perfil incluye preferencias opcionales inicialmente vacías y propuestas locales. Consulta [mejoras y personalización](references/improvements.md). Las publicaciones excluyen datos del usuario desde el origen; actualizar conserva su perfil.

## Distribución

Hay dos formatos. El proyecto descargable contiene `AGENTS.md` y `.agents/skills/`; el usuario lo abre como carpeta local y envía el primer mensaje. El plugin opcional conserva `plugin.json` y `skills/` para su proceso de instalación. El descubrimiento de skills y las operaciones del navegador deben comprobarse en el cliente. Publicar un plugin en el directorio requiere su revisión.

No copies perfiles, recibos, archivos de credenciales o sesiones dentro del paquete. Mantén el perfil en una ubicación privada fuera del directorio instalado para conservarlo entre actualizaciones.

Formato: [documentación de paquetes de OpenAI](https://developers.openai.com/plugins/build/plugins).
