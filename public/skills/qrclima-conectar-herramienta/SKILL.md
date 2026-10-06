---
name: qrclima-conectar-herramienta
description: Habilita el conector propio de QRclima al escribir inicia y guía la autorización en el navegador. Úsala para consultar datos de la organización, actualizar perfil o marca y guardar foto, logo o constancia con permisos específicos.
---

# Conectar y completar los datos de QRclima

Lee la [guía del conector](../../references/connector.md) y el [criterio de conexión fiable](../../references/connection-acceptance.md). Al recibir «inicio» o «inicia», prioriza comprobar el acceso antes de una entrevista extensa; el comando del cliente sigue siendo `inicia`. Comprueba un runtime Python 3.10 o posterior y la carpeta del proyecto. Usa el Python disponible en el cliente antes de instalar otro. Si falta, guía su instalación para el sistema operativo real; no necesitas Node, Firebase CLI, cuenta de servicio ni una VM en el equipo del usuario.

Desde la carpeta descargada ejecuta `python .agents/scripts/connector.py --root .qrclima inicia`. Desde las fuentes el script está en `public/scripts/connector.py`. Si ya existe una conexión, usa `status` en lugar de crear otra. No leas ni imprimas el archivo de conexión. La salida incluye un enlace de autorización y un código público; explica que el usuario debe iniciar sesión y revisar permisos en esa página. Nunca pidas contraseñas, tokens, cookies o códigos MFA en el chat.

El usuario elige organización y permisos. Espera a que regrese; no consultes en bucle mientras usa el navegador. Cuando diga «continúa», ejecuta `status`. El script conserva UID y organización comprobados en el perfil `principal`, sin ampliar políticas comerciales. Si cambia la organización o revoca el acceso, vuelve a conectar; editar el perfil local no modifica los permisos del servidor.

Después de un `status` satisfactorio, comprueba una lectura actual limitada dentro del alcance concedido. Informa por separado autorización, lectura y capacidad de escritura de cada operación. Una escritura requiere petición concreta y relectura; «inicia» no autoriza cambios reales de prueba. No declares configuración completa de lectura y escritura cuando solo verificaste el navegador, permisos o archivos locales. Conserva como pendiente la escritura que no tenga evidencia.

Después de acreditar lectura y escritura, realiza el [reconocimiento mínimo](../../references/initial-discovery.md) dentro del mismo inicio: recupera datos básicos de cuenta y comprueba presencia con hasta un registro por categoría autorizada, sin páginas adicionales ni descargas. No pidas una segunda orden para esa etapa.

Cuando el usuario solicite importar el negocio, o una tarea concreta necesite más registros, aplica `qrclima-sincronizar-contexto` con ese alcance. `sync --max-pages 3` después de `--root .qrclima` guarda páginas privadas; no es el reconocimiento por defecto de «inicio». Usa el índice local para localizar registros y las consultas del conector para confirmar estado actual. Algunas categorías necesitan el portal: los documentos del conector no equivalen a todos los PDFs históricos. Conserva cursores y cobertura parcial en una carga ampliada.

Pide únicamente los faltantes que afectan a la tarea. Si ya existe nombre, empresa, logo o datos fiscales, no vuelvas a pedirlos. Una VM se pregunta solo si el usuario elige una integración externa que la necesita. Una constancia es opcional; leerla no autoriza configurar un emisor ni facturar.

Ante «guarda esta foto de perfil», revisa que el archivo pertenezca al destino solicitado y que el permiso esté habilitado. Lee `status`, toma `profileRevision`, genera un ID único del intento y usa `upload profile_photo --file <ruta> --revision <revision> --request-id <id> --confirmed`. Para logo usa `organization_logo` y `organizationRevision`; exige permiso de propietario. Para constancia usa `constancia`, sin revisión de perfil: el PDF se guarda como documento privado, no cambia datos fiscales.

Para cambiar campos de perfil o marca, prepara un JSON privado con `patch`, `expectedRevision`, `requestId`, `confirmed`. Usa `update profile|branding --input <archivo>`. La instrucción concreta del usuario autoriza el cambio que pidió; si faltan datos o el destino es ambiguo, acláralos. No conviertas la autorización inicial de una herramienta en una orden para alterar todos sus datos.

Relee después: `status` para perfil/marca, `read documents` para constancia y `download` si necesitas comprobar su contenido. Conserva intento y recibo privados. Un conflicto exige revisar el estado; una respuesta incierta exige conciliar el intento existente, sin inventar otro ID. Nunca escribas ventas, citas, cobros, impuestos, plan, roles o inventario mediante esta API; aplica sus skills y los flujos del portal.

Si el conector todavía no está habilitado, informa configuración parcial, identifica el bloqueo y ofrece continuar por la sesión del portal disponible. No la eludas con credenciales administrativas. La alternativa por portal no cierra el requisito del conector para 1.0.0. Si el cliente no puede ejecutar Python ni manejar archivos, no afirmes compatibilidad operativa.
