# Entrevista inicial y descubrimiento de contexto

La entrevista se adapta a la primera tarea. Haz una pregunta breve por turno o agrupa dos o tres datos relacionados cuando resulte sencillo responderlos. Guarda respuestas útiles al recibirlas; no esperes a completar todo el cuestionario. Mantén nulos los datos que todavía no sean necesarios.

## 1. Elegir una primera tarea

Si el usuario pidió configurar y conocer el negocio, empieza por conectar su cuenta. Si todavía no eligió un alcance, pregunta: «¿Quieres configurar e importar el contexto del negocio, o resolver primero una venta, cita o consulta?».

Después solicita un alias para el perfil, idioma y zona horaria únicamente si faltan. Un nombre no identifica una cuenta. Explica la ruta privada donde se guardará el perfil y permite elegir otra. No crees chats adicionales por responder esta entrevista.

## 2. Conectar la cuenta propia

En el proyecto descargable, «inicia» aplica primero `qrclima-conectar-herramienta`. El agente abre la autorización del portal, el usuario elige la organización y vuelve al chat. `status` incorpora la identidad comprobada; `sync` carga contexto privado por etapas. Consulta [el conector](connector.md). Si el servicio está deshabilitado, continúa por la sesión del navegador disponible sin solicitar acceso administrativo.

Pregunta: «¿Ya puedes entrar al portal de QRclima y qué organización quieres utilizar?».

El usuario inicia sesión en el navegador. Comprueba la organización seleccionada y los datos de cuenta, rol y plan que realmente pueda mostrar el portal o una herramienta autorizada. No pidas al usuario un UID, el nombre de una colección de Firestore ni una llave de servicio para resolver el acceso. Si no puedes comprobar una identidad técnica requerida por el contrato de operación, registra ese faltante y conserva el borrador; no inventes el identificador.

Para comprender sus datos, aplica la [carga inicial](synchronization.md) al alcance solicitado: empresa, clientes, conceptos, citas, cotizaciones y documentos accesibles. Prioriza lo necesario para una primera tarea y conserva alcance y pendientes por etapa. QRclima sigue siendo la fuente actual; los registros se indexan por organización fuera del perfil. La importación no permite otras colecciones, organizaciones o secretos.

## 3. Completar el entorno necesario

Si hay archivos en la tarea, pregunta: «¿Qué carpeta quieres usar para tus comprobantes?».

Comprueba la carpeta mediante una lectura local cuando exista esa herramienta. La respuesta queda como declarada hasta verificarla. No conviertas una ruta en un comando ni crees una estructura de archivos adicional que el usuario no haya pedido.

La VM es opcional. Cuando el usuario elige una integración que la necesita, pregunta: «¿Ese servicio está en una máquina virtual? ¿Qué host o proveedor usas y para qué servicio?».

Guarda finalidad y referencia a una conexión existente. Una respuesta no demuestra conectividad ni autoriza exploración del servidor. Si el usuario no usa VM, guarda `used: false` como dato declarado y continúa con el portal.

## 4. Preparar un resultado pequeño

Si la petición inicial es configurar, entrega el estado de la carga y los faltantes. Si hay una primera tarea, prepara un borrador con sus campos reales. Para una venta, determina cliente, conceptos, cantidades, precios y fechas, además de lo efectivamente cobrado. No deduzcas que «vendí» significa «cobré».

La configuración termina mostrando:

- Perfil y ruta privada, sin imprimir todos sus valores.
- Cuenta y organización comprobadas, o el faltante concreto.
- Datos declarados y conexiones verificadas.
- Borrador inicial y qué falta para registrarlo.

Habilitar registros reales se trata mediante el [contrato de ejecución](runtime.md), con la instrucción del usuario y los permisos de QRclima. El perfil parcial es válido; no conviertas todas las preguntas opcionales en requisitos de entrada.

## Volver a usarlo

Todos los chats leen el mismo perfil y su revisión. Cuando el usuario aporta una corrección, actualiza el campo pertinente con su fuente. Recomprueba sesión, permisos y datos comerciales cuando dependan de ellos las operaciones. El cambio de organización requiere una comprobación nueva.

Las preferencias expresas pueden conservarse. Una regla inferida, como «este cliente siempre paga al final», queda como propuesta y no se aplica automáticamente. El agente no aprende en segundo plano ni escucha otras conversaciones por instalar el paquete.
