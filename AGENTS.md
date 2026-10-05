# Mantener el kit público de QRclima

Esta es la raíz de desarrollo, no un perfil comercial. Lee README.md y CONTRIBUTING.md. Las fuentes operativas están en `public/`, la carpeta de uso se construye con `starter/` y `tools/build_package.py`. No conectes datos del mantenedor solo por abrir el repositorio. Trabaja en una carpeta generada para el uso personal.

Al mejorar el kit, clasifica el cambio: global, personal, mixto o pendiente de evidencia. Reproduce correcciones globales con datos ficticios. Una preferencia particular se guarda en el perfil privado; su extensión general puede añadir un parámetro vacío. No conviertas una instrucción comercial particular en una regla de todos los usuarios.

Las skills tienen una fuente común. Claude usa entradas generadas que remiten a esa fuente; no dupliques la lógica. Perfiles, propuestas originales, contexto, recibos, documentos, sesiones, secretos y rutas del equipo pertenecen a almacenamiento privado excluido de Git. No copies conversaciones ni capturas reales a issues o ejemplos. Lee `public/references/improvements.md` cuando el alcance sea ambiguo.

Antes de publicar, ejecuta los controles pertinentes, `python tools/check_public.py --tracked --history` y revisa el diff preparado. Usa rutas explícitas al preparar Git. No fuerces la inclusión de una carpeta privada. Una comprobación automática no detecta toda información personal: revisa manualmente el contenido público.

No anuncies versión 1 hasta cumplir `docs/VERSION-1.md`. No deduzcas compatibilidad operativa de la existencia de un adaptador. Las instrucciones humanas vigentes y los permisos reales prevalecen sobre preferencias o propuestas guardadas. Mejorar este kit no autoriza modificar o desplegar la aplicación QRclima.
