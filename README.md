# Asistente de QRclima

Un asistente configurable para consultar QRclima, preparar ventas, organizar citas y revisar finanzas mediante conversación natural. **Piloto público 0.3.0; todavía no es la versión 1 estable.**

Descarga [la versión empaquetada](https://github.com/galjoctavio-ux/qrclima-assistant/releases/tag/v0.3.0), descomprime `qrclima-asistente-0.3.0.zip` y abre `EMPIEZA-AQUI.html`. El ZIP del asistente está preparado para uso; el botón **Code → Download ZIP** de GitHub descarga las fuentes de desarrollo.

## Una carpeta, una conversación

Abre la carpeta descargada en un agente con archivos locales, Python 3.10 o posterior y navegador conectado. Envía:

> Configura mi asistente de QRclima en esta carpeta. Lee AGENTS.md, ayúdame a conectar mi sesión y conoce la información accesible de mi organización: empresa, clientes, conceptos, citas, cotizaciones y documentos. Guarda el contexto local con sus fuentes y pregúntame solo lo que falte. La configuración inicial es de lectura; después te pediré las operaciones que necesite.

El usuario inicia sesión en el portal con su propia cuenta. El asistente reutiliza datos comprobados, pregunta por faltantes y conserva alcance y fecha. Los registros reales respetan permisos, plan y validaciones de QRclima. El kit no utiliza Firebase Admin ni evita bloqueos del portal.

## Agentes y capacidades

Incluye entradas para Codex, Claude Code, Gemini CLI y Kimi Code CLI, y lectura explícita para hosts con DeepSeek u otros modelos. Todos comparten ocho procedimientos: asistente, configuración, perfil, contexto, ventas, agenda, finanzas y mejoras. Consulta la [compatibilidad y sus límites](starter/COMPATIBILIDAD.md).

El kit no proporciona suscripciones de inteligencia artificial, llaves API, navegador ni acceso móvil por sí mismo. Un modelo que lee Markdown no necesariamente puede ejecutar tareas. La compatibilidad de archivos se ha comprobado; las operaciones en cada cliente requieren pruebas reales. SDK, WhatsApp, CFDI, inventario y pagos bancarios quedan fuera del alcance inicial.

## Personalización y mejoras

Cada usuario comienza sin nombre, organización, rutas, VM ni preferencias heredadas. Hay espacios vacíos para estilo de respuesta, navegador, nombres de documentos, duración de citas y pie de cotizaciones; son opcionales y ampliables.

La skill `qrclima-mejorar-asistente` clasifica las mejoras como globales, personales, mixtas o pendientes de evidencia. Los valores y evidencias privados quedan en `.qrclima/`, fuera de Git. Las correcciones generales se reproducen con datos ficticios y se incorporan al procedimiento común. La versión 1 se construirá desde fuentes públicas; actualizar no elimina los datos del usuario. Lee [cómo contribuir](CONTRIBUTING.md) y [el camino a versión 1](docs/VERSION-1.md).

## Desarrollar y construir

Este repositorio contiene fuentes. Las carpetas de uso se generan aparte:

```text
public/          skills, referencias, contratos y scripts comunes
starter/         instrucciones y guía de la carpeta descargable
tools/           construcción y comprobación de publicación
tests/           comprobaciones locales con datos ficticios
docs/            decisiones y criterios de versión 1
workspace/       carpetas generadas, excluidas de Git
.qrclima/        datos privados, excluidos de Git
```

Desde la raíz, con Python 3.10 o posterior:

```sh
python -m unittest discover -s tests -q
python tools/check_public.py
python tools/build_package.py --format workspace --workspace-dir ./workspace/Mi-asistente-QRclima-0.3 --output ./dist/qrclima-asistente-0.3.0.zip
```

El constructor rechaza destinos existentes; elige una ruta nueva para otro ensayo. El ZIP se genera únicamente con las fuentes públicas y la plantilla. Para revisar el contenido que entrará a Git, utiliza `python tools/check_public.py --tracked` después de preparar el índice. El escáner reconoce rutas no permitidas y formatos conocidos de secretos; no sustituye revisar textos y capturas.

El formato de plugin es opcional: `python tools/build_package.py --format plugin --output ./dist/qrclima-plugin-0.3.0.zip`. Construirlo no instala ni registra un plugin en un directorio público.

Consulta [arquitectura](ARCHITECTURE.md), [casos de aceptación](acceptance.md), [verificación](verification.md), [guía de primer uso](starter/README.md) y [licencia MIT](LICENSE).
