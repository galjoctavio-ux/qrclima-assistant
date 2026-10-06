# Mejoras comunes y personalización

El procedimiento público debe funcionar con una empresa ficticia y sin conocer al mantenedor. Las preferencias cambian valores; no conceden permisos ni sustituyen validaciones de QRclima.

| Clasificación | Ejemplo | Destino |
|---|---|---|
| `global` | Evitar una venta duplicada después de un guardado incierto | Skill o helper común, con caso ficticio |
| `personal` | Mi navegador, mi ruta de documentos o mi firma | `preferences`, perfil o contexto privado |
| `mixed` | Permitir una firma configurable y guardar mi firma concreta | Parámetro vacío compartido y valor privado |
| `needs_evidence` | Una pantalla parece bloquear una función sin haberlo comprobado | Propuesta privada pendiente de reproducción |

## Espacios configurables

Un perfil nuevo tiene preferencias vacías: `response-style`, `preferred-browser`, `documents-naming`, `appointment-duration-minutes` y `quotation-footer`. Sus valores son `null`, estado `unknown`; no se heredan del piloto. Puedes añadir claves de configuración específicas, con el mismo contrato. No hace falta llenarlas todas para comenzar.

Cada preferencia tiene `key`, `organization_id` y `setting` con valor, estado, fuente y fechas. Alcance nulo significa este perfil personal, no todas las personas. Una preferencia de organización se aplica solo al ID correspondiente. La preferencia específica prevalece sobre la del perfil; un valor `unknown` no impone un valor por defecto. Ninguna preferencia habilita SDK, mensajes, facturas, operaciones o herramientas. Antes de usar una duración, firma o ruta, comprueba que sea pertinente y válida para la tarea.

Durante el desarrollo pueden usarse las claves opcionales `project-role` y `assistant-role`. Sus valores públicos iniciales son nulos, estado `unknown`; el papel que declare una persona se guarda solo en `preferences` de su perfil. Estas claves no conceden propiedad de una organización, acceso técnico ni permisos de publicación.

Las nuevas claves que merezcan un espacio de configuración común se documentan con valor vacío. No copies al paquete el catálogo, horarios, precios o reglas particulares de una empresa para hacerlo funcionar.

## Registro privado de propuestas

`improvement_proposals` conserva ID, clasificación, descripción, estado, evidencia privada y `public_summary` opcional. Actualiza la lista completa después de releer la revisión; usa `profile_store.py apply`, no edites un perfil antiguo. El validador comprueba estructura y bloquea formatos conocidos de secretos; no determina si una mejora es global ni anonimiza el texto.

Promover una mejora significa incorporar y verificar su parte común en el repositorio. No significa publicar el expediente privado. Redacta un resumen público con datos ficticios y revisión humana antes de compartir. Nunca adjuntes el perfil, el historial de conversación, una captura real o el diario privado como prueba pública.

## Versiones y datos privados

La publicación se construye desde las fuentes públicas permitidas. El piloto mantiene sus datos fuera de Git desde el primer commit. Una versión nueva conserva el perfil existente; no lo limpia ni lo elimina. La versión 1 será una distribución nueva con campos personales vacíos. Borrar archivos de una rama no elimina datos del historial de Git.

Las mejoras en una carpeta de uso y las mejoras en el repositorio no se sincronizan solas. Lleva una corrección general al repositorio mediante un parche o contribución revisada; conserva las preferencias en la carpeta privada. La versión 1 necesita pruebas reales de uso, además de validadores de archivos.

El registro público de requisitos y criterios de aceptación está en [PENDIENTES-1.0.0.md](../PENDIENTES-1.0.0.md). Los detalles privados y las preferencias siguen en el perfil. Un requisito documentado no cierra una prueba ni elimina un bloqueo de publicación.
