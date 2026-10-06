---
name: qrclima-configurar-perfil
description: Configura por primera vez el perfil privado y el acceso propio a QRclima mediante una entrevista progresiva. Úsala al iniciar el paquete o comprobar qué falta para una primera tarea.
---

# Configurar perfil de QRclima

Lee el [contrato de ejecución](../../references/runtime.md), la [entrevista progresiva](../../references/onboarding.md) y el [criterio de conexión fiable](../../references/connection-acceptance.md). La configuración registra datos personales y de entorno; no autoriza operaciones comerciales. Prioriza resolver el acceso y su alcance antes de una entrevista extensa.

Empieza por conectar y conocer el negocio cuando esa sea la petición, o por la tarea concreta del usuario. Identifica o crea su perfil privado con el administrador local. En el proyecto descargable usa `.qrclima` y alias `principal` salvo elección distinta. Consulta primero los datos disponibles de su sesión; pide únicamente los que falten para el siguiente paso. Reutiliza respuestas previas, marcándolas como declaradas hasta tener evidencia de verificación.

Comprueba el controlador de navegador disponible y el acceso al portal. El usuario realiza su inicio de sesión en la interfaz. Lee la cuenta y organización seleccionadas; registra UID cuando esté observado, o `account_reference` como cuenta visible sin inventar un UID. Registra organización, rol y plan con la precisión de la evidencia. Si no hay acceso, conserva el perfil parcial y explica el dato o conexión que impide seguir.

Pregunta por una VM solo cuando el servicio elegido dependa de ella. Guarda host, finalidad y referencia a un acceso existente; nunca secretos. No exijas VM, Firestore, SDK o WhatsApp para comenzar con el portal.

Antes de agregar organizaciones, comprueba si el mismo ID ya está registrado. Al seleccionar otra organización, no traslades datos ni autorizaciones de la anterior. Actualiza usando la revisión leída.

Después de verificar lectura y escritura en el caso de inicio, continúa con el [reconocimiento mínimo](../../references/initial-discovery.md) sin pedir otra orden: recupera el nombre y datos básicos disponibles, y comprueba presencia y lectura de las categorías autorizadas mediante muestras de hasta un registro. No uses una importación masiva como comprobación de existencia ni preguntes por datos de perfil que ya se puedan recuperar.

Aplica `qrclima-sincronizar-contexto` cuando el usuario pidió importar la información del negocio. Finaliza con la ruta privada, los datos declarados/comprobados, las categorías consultadas y los pendientes. Distingue sesión del portal, conector autorizado, lectura y escritura por operación; indica configuración parcial si falta evidencia del alcance solicitado. No hagas una venta o cita real como prueba de configuración. Los contratos están en [perfil](../../schemas/profile.schema.json) y [adaptadores](../../references/adapters.md).
