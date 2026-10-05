# Carga inicial del negocio y consultas posteriores

## Acceso

La primera versión usa el portal con una sesión propia en `@Chrome`, otro navegador compatible o `@Browser`. El usuario inicia sesión y acepta los permisos del cliente. El asistente no instala Firebase CLI, SDK administrativo ni importa una cuenta de servicio para esa vía.

Un SDK de lectura futuro necesitaría autenticación individual y consultas limitadas por organización. Se mantiene fuera de esta entrega; tener la configuración pública de Firebase no autentica una cuenta ni conserva todas las restricciones de la interfaz.

## Recorrido inicial

| Etapa | Información | Resultado local |
|---|---|---|
| Empresa | Cuenta visible, organización, rol/plan, nombre, marca, logo y datos fiscales visibles | Perfil y snapshot de empresa |
| Catálogos | Clientes y conceptos accesibles | Registros identificables y cobertura por página o filtro |
| Agenda | Citas del periodo consultado y configuración visible | Fechas, estados, técnicos y alcance temporal |
| Cotizaciones | Folios, clientes, fechas, partidas y estados accesibles | Índice; detalle cuando esté consultado |
| Documentos | PDFs existentes, documentos aportados y referencias de imágenes | Metadatos y ruta local si se obtuvo el original |

La petición de conocer el negocio permite recorrer estas etapas. Para una primera tarea se priorizan sus registros necesarios y después se continúa con el resto solicitado. Si el volumen no cabe en el turno, registra el último filtro/página y los pendientes; continúa al retomar la conversación. No programes un trabajo de fondo por iniciativa propia.

Una cobertura `complete` se refiere exclusivamente al `scope` descrito, por ejemplo «citas visibles de octubre». No equivale a toda la agenda histórica. Paginas diferentes pueden guardarse como snapshots separados. El índice combina IDs observados para la búsqueda, pero no prueba ausencia ni eliminación de registros.

## Identidad y fuentes

El snapshot requiere la organización activa registrada en el perfil y comprobada desde una fuente autorizada. Para identificar la cuenta usa el UID comprobado cuando esté disponible, o `account_reference` con una referencia estable del perfil autenticado, como el correo visible en su sesión. No sustituyas el UID por un correo en el campo `actor_uid`.

El administrador local comprueba concordancia con el perfil. No autentica la fuente ni reemplaza los permisos de QRclima. Si no puedes comprobar los identificadores necesarios con las herramientas disponibles, conserva el contexto como pendiente y explica esa limitación. No pidas al usuario conocer colecciones o secretos para solventarla.

## Guardar y buscar

Desde la carpeta de recursos del paquete, usa:

```text
context_store.py status --profile <alias> --root <directorio-privado>
context_store.py put --profile <alias> --root <directorio-privado> --expected-revision <n> --file <snapshot-json>
context_store.py search --profile <alias> --root <directorio-privado> --category clients --term <texto-o-terminacion>
```

`put` guarda un snapshot inmutable y actualiza un índice atómico por organización. Un ID de snapshot existente o una revisión antigua se rechaza. Los datos se guardan dentro de `profiles/<alias>/context/`, fuera de las skills, y las consultas están acotadas. La organización activa se vuelve a comprobar después de cambiar de cuenta u organización.

## Documentos y faltantes

Un documento pendiente no impide las tareas que no lo necesitan. Pregunta por razón social o constancia cuando falten datos fiscales relevantes; no lo hagas obligatorio para preparar una cita. Guarda la evidencia y distingue el emisor del receptor. El paquete inicial no emite CFDI ni actualiza la configuración fiscal.

La pantalla de cotizaciones del portal puede generar PDFs consumiendo cupo. Indexar una cotización y descargar un PDF ya existente son alcances distintos de generar uno nuevo. Si solo hay un botón generador, registra «PDF por generar» y resuelve esa generación como tarea explícita.

Una cita recién registrada requiere lectura actual del portal aunque el índice haya sido cargado minutos antes. Una búsqueda local vacía significa «no encontrado en lo indexado», y requiere consulta actual cuando determine una decisión comercial.
