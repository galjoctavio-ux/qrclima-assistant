import { auth } from '@/lib/firebase-client';

export interface AssistantState {
  uid: string;
  organizationId: string;
  owner: boolean;
  organization: { name?: string; plan?: string };
}
export interface AssistantConnection {
  id: string;
  label: string;
  scopes: string[];
  expiresAt: number;
  revoked: boolean;
}
export async function assistantRequest<T>(input: Record<string, unknown>): Promise<T> {
  const endpoint = process.env.NEXT_PUBLIC_QRCLIMA_ASSISTANT_API_URL;
  if (process.env.NEXT_PUBLIC_QRCLIMA_ASSISTANT_ENABLED !== 'true' || !endpoint) {
    throw new Error('La herramienta todavía no está habilitada en QRclima.');
  }
  const user = auth.currentUser;
  if (!user) throw new Error('Inicia sesión con tu cuenta de QRclima.');
  const response = await fetch(endpoint, {
    method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: ['Bearer', await user.getIdToken(true)].join(' ') },
    body: JSON.stringify(input), cache: 'no-store', redirect: 'error',
  });
  const payload = await response.json();
  if (!response.ok) {
    const messages: Record<string,string> = {
      reauth_required: 'Vuelve a iniciar sesión aquí para autorizar una conexión nueva.',
      permission_denied: 'Tu cuenta, organización o plan no permite esta conexión.',
      already_exists: 'Esta solicitud ya se utilizó. Inicia una nueva conexión desde tu carpeta.',
      resource_exhausted: 'Alcanzaste el límite. Revoca una conexión anterior o intenta más tarde.',
    };
    throw new Error(messages[payload?.error?.code] || 'No se completó la conexión. Intenta de nuevo cuando QRclima esté disponible.');
  }
  return payload.result as T;
}
