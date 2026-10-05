# Integración en el portal QRclima

`web/` contiene archivos nuevos para el proyecto Next.js de QRclima. Copia sus rutas `app/` y `lib/` al checkout aislado del portal. No reemplaces `lib/auth-context.tsx`: aplica únicamente la excepción del guard de sesión descrita abajo, respetando sus cambios actuales.

## Entrada de sesión

En `AuthProvider`, la rama `if (!firebaseUser)` actualmente redirige a `/login`. La página del asistente contiene su propia entrada mediante los métodos existentes del contexto. Conserva el enlace de autorización cambiando solo el guard:

```tsx
if (pathname !== '/login' && pathname !== '/assistant/connect') router.push('/login');
```

Este cambio deja accesible la pantalla de autorización antes del login. No da acceso a datos: la sesión Firebase y el servidor comprueban el usuario y permisos. El formulario utiliza `login`/`loginWithGoogle` existentes; una autorización nueva requiere sesión reciente. Una sesión antigua puede verificarse de nuevo con contraseña o Google.

La pantalla muestra cuenta, organización, código, permisos opcionales, caducidad y conexiones revocables. Inicia con lectura y ningún permiso de escritura marcado. El propietario puede habilitar marca; el administrador no obtiene esa opción. Seleccionar otro negocio usa `switchOrg` existente y reinicia permisos y confirmación.

## Configuración

Configura en el entorno del portal:

- `NEXT_PUBLIC_QRCLIMA_ASSISTANT_API_URL`: URL HTTPS verificada de la función.
- `NEXT_PUBLIC_QRCLIMA_ASSISTANT_ENABLED`: `true` para activar el piloto, ausente/`false` para desactivar.

La URL y flag son configuración pública, no credenciales. El cliente consulta `/assistant/connector-config` sin cachear. El servidor debe permitir el mismo origen HTTPS exacto por CORS. Nunca introduzcas un token, clave de servicio o llave de IA en `NEXT_PUBLIC_*`.

QRclima usa `basePath: '/qrclima'`: las URLs publicadas son `/qrclima/assistant/connect` y `/qrclima/assistant/connector-config`. Los guards y rutas internas del router conservan `/assistant/connect`; no añadas el prefijo dos veces.

## Validación de salida

Comprueba TypeScript y build, entrada por correo y Google conservando `request`, organización visible, autorización y renovación, permisos de propietario/admin, consentimiento sin casillas de escritura preseleccionadas, revocación y ancho móvil. La pantalla no envía contraseñas al agente: el usuario las introduce en el portal autenticado.

La implementación está preparada para integrarse; hasta que este portal y el servidor estén publicados y habilitados, el ZIP no puede conectarse por sí solo. No promociones versión 1 basándote únicamente en archivos o tests de emuladores.
