# Elegir tu agente

El kit comparte procedimientos en Markdown y archivos JSON. El modelo comprende instrucciones; la aplicación que lo ejecuta aporta archivos, Python, navegador y permisos. Una suscripción, API o cuota del proveedor no viene incluida en QRclima ni en este repositorio.

| Entorno | Entrada preparada | Comprobación necesaria |
|---|---|---|
| Codex local | `AGENTS.md`, `.agents/skills/` | Reconocer skills, runtime local y navegador con sesión propia |
| Claude Code | `CLAUDE.md` importa `AGENTS.md`; `.claude/skills/` enlaza los procedimientos comunes | Ver las skills y conectar un controlador de navegador compatible |
| Gemini CLI | `GEMINI.md` importa `AGENTS.md`; `.agents/skills/` | Carpeta de confianza, `/skills list`, consentimiento y navegador |
| Kimi Code CLI | `AGENTS.md`, `.agents/skills/` | Descubrimiento por versión, raíz del proyecto y navegador |
| Agente con DeepSeek | Leer `AGENTS.md` y la skill requerida | El host debe ejecutar archivos, scripts y herramientas; la API sola no lo hace |
| Otro agente | Lectura explícita de `AGENTS.md` y archivos `SKILL.md` | Comprobar capacidades y autenticación del host antes de operar |

Abre o inicia tu agente **dentro de esta carpeta**. Si no carga instrucciones automáticamente, envía el mensaje inicial del README y pídele leer esos archivos. Las entradas de Claude contienen enlaces al procedimiento original; las referencias de este se resuelven desde `.agents/skills/<nombre>/SKILL.md`.

Kimi documenta el descubrimiento de skills de proyecto tomando como raíz el directorio `.git` más cercano. Si tu versión lo requiere y descargaste un ZIP, puedes ejecutar `git init` en esta carpeta para crear un repositorio local, sin remoto ni publicación. Comprueba después qué skills encontró. No hagas un commit de `.qrclima/`.

Las menciones `@Browser` y `@Chrome` de la guía son propias del cliente que las ofrece. En otros clientes utiliza su controlador real y su documentación. No instales herramientas arbitrarias ni extraigas cookies para simular una sesión. Si falta navegador, puedes configurar el perfil y preparar borradores con la información que proporciones; el registro real queda pendiente.

El kit no instala estos clientes, no configura proveedores de modelos y no crea una conexión propia con WhatsApp o Firebase. Un chat web de texto, incluso si acepta un ZIP, puede carecer de las herramientas necesarias. El uso por voz o desde un teléfono depende de una sesión conectada al equipo que ejecuta el agente.

## Estado de compatibilidad

En 0.3.0 se validan archivos, referencias, scripts y empaquetado. Los adaptadores se basan en documentación oficial; **no se han certificado operaciones reales en todos estos clientes**. Informa cliente, versión, herramientas y resultado cuando pruebes el kit; no deduzcas compatibilidad operativa de que el modelo pudo leer una skill.

Fuentes consultadas el 5 de octubre de 2026: [Codex skills](https://learn.chatgpt.com/docs/build-skills), [Claude instrucciones](https://code.claude.com/docs/en/memory), [Claude skills](https://code.claude.com/docs/en/skills), [Gemini contexto](https://geminicli.com/docs/cli/gemini-md/), [Gemini skills](https://geminicli.com/docs/cli/using-agent-skills/), [Kimi skills](https://moonshotai.github.io/kimi-code/en/customization/skills.html), [DeepSeek herramientas](https://api-docs.deepseek.com/guides/tool_calls/).
