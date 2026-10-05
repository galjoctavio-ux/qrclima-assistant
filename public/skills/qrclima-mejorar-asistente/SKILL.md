---
name: qrclima-mejorar-asistente
description: Clasifica y aplica mejoras al asistente de QRclima distinguiendo procedimientos generales de preferencias privadas. Úsala al corregir el kit, proponer una mejora global o aprender una preferencia personal; no para modificar la aplicación QRclima.
---

# Mejorar el asistente

Lee el [contrato de ejecución](../../references/runtime.md) y la [separación de mejoras](../../references/improvements.md). Identifica si estás en el repositorio de desarrollo o en una carpeta de uso. Una corrección al kit no autoriza desplegar QRclima, enviar mensajes ni publicar datos.

Clasifica la petición como `global`, `personal`, `mixed` o `needs_evidence`. Da una razón concreta. Una preferencia del usuario se guarda en `preferences` del perfil privado; un hecho del negocio queda en perfil o contexto, con fuente. No copies valores privados a skills, ejemplos o archivos de instrucciones compartidos.

Registra la propuesta en `improvement_proposals` del perfil mediante `profile_store.py apply` y revisión vigente. Conserva detalles y evidencias privadas allí. Si la petición es mixta, separa la mejora reutilizable, un parámetro público vacío y el valor privado. Si es una suposición del modelo, mantenla propuesta hasta tener evidencia o instrucción suficiente.

Para una corrección global autorizada, reproduce el problema con datos ficticios. Modifica el procedimiento compartido y sus recursos, conserva el comportamiento compatible y comprueba el resultado. Los adaptadores referencian el mismo procedimiento. La existencia de una entrada o el estado escrito `validated` no prueba pruebas ejecutadas.

En el repositorio, documenta el cambio sin datos del piloto, ejecuta las comprobaciones pertinentes y `python tools/check_public.py` antes de compartir. En una carpeta descargada, registra la corrección como propuesta local o parche revisable: esa carpeta no incluye las herramientas de publicación del repositorio. No prometas enviar mejoras a GitHub desde el ZIP ni sincronizar carpetas automáticamente.

Informa clasificación, archivos compartidos cambiados, campos privados cambiados y evidencia de verificación. Deja `public_summary` nulo hasta redactar y revisar una descripción pública sin identidad, rutas, clientes, registros ni documentos reales. Compartir una propuesta requiere la instrucción del usuario para esa publicación.
