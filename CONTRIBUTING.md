# Mejorar el asistente

Cualquier persona puede adaptar el kit, proponer un issue o enviar un pull request. La licencia MIT permite usar y modificar instrucciones y scripts; el acceso a QRclima y al proveedor de inteligencia artificial tiene sus propias condiciones.

## Distinguir el cambio

Una mejora global corrige un comportamiento reproducible o aporta una capacidad útil con parámetros genéricos. Una preferencia modifica cómo trabaja un usuario o empresa. Si hay ambos elementos, separa el mecanismo general, su valor inicial vacío y el valor privado. Usa [el contrato de mejoras](public/references/improvements.md).

Ejemplo: «agregar una firma configurable a un borrador» puede ser general. El nombre, teléfono, dirección y firma concreta pertenecen al perfil privado. La misma separación aplica a VM, carpetas, precios, horarios y mensajes técnicos.

## Trabajar durante el piloto

1. Usa una carpeta generada para tus operaciones. Conserva su `.qrclima/` al actualizar instrucciones.
2. Registra propuestas y evidencia original en el perfil privado. El agente declara clasificación y razón; si faltan pruebas no las inventa.
3. Lleva la parte común al repositorio con un caso ficticio. No copies el perfil completo para «anonimizarlo después».
4. Comprueba el resultado, revisa el diff y comparte únicamente código, procedimiento y reproducción públicos. Las propuestas locales no se sincronizan automáticamente.

## Contenido de una contribución

Explica el problema, cómo reproducirlo con datos ficticios, qué cambia y cómo lo comprobaste. Indica cliente, versión y herramientas cuando dependa de un agente. No adjuntes clientes reales, correos personales, PDFs, IDs comerciales, datos fiscales, capturas de sesiones ni conversaciones originales. Un fallo de lectura local no prueba un fallo del portal.

Las funciones nuevas respetan organización y sesión activas, validaciones del portal, autorización vigente, separación venta/cobro y verificación posterior. El perfil local no concede permisos. Un SDK nuevo requiere diseñar y verificar autenticación y acceso por usuario; no uses Firebase Admin como sustituto del portal.

## Comprobar antes de compartir

```sh
python -m unittest discover -s tests -q
python tools/check_public.py
```

Construye el ZIP en una ruta nueva, examina sus archivos y prepara Git con rutas explícitas. Después:

```sh
python tools/check_public.py --tracked --history
git diff --cached
```

`.gitignore` no elimina un dato ya incluido en Git. El control revisa el índice y, con `--history`, archivos del historial disponible; no certifica anonimato semántico. Una corrección no justifica eliminar datos privados existentes.

## Prioridad de versión 1

Conserva la visión inicial: una carpeta, una conversación, cuenta propia, entrevista corta y procedimientos fiables. Primero configuración, consulta, venta sencilla y cita. Los conectores avanzados o más agentes necesitan beneficio comprobado; no desplacen las pruebas de los flujos básicos. Consulta [VERSION-1.md](docs/VERSION-1.md).
