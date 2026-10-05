'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { assistantRequest, AssistantState, AssistantConnection } from '@/lib/assistant-bridge';

const permissions = [
  { id: 'profile.write', label: 'Actualizar mi nombre, ciudad, teléfono y foto' },
  { id: 'branding.write', label: 'Actualizar nombre de empresa, logo y presentación de PDFs' },
  { id: 'documents.write', label: 'Guardar documentos privados, como mi constancia fiscal' },
];

export default function AssistantConnectPage() {
  const { user, organizationId, memberships, loading, login, loginWithGoogle, switchOrg } = useAuth();
  const [requestId, setRequestId] = useState('');
  const [state, setState] = useState<AssistantState | null>(null);
  const [connections, setConnections] = useState<AssistantConnection[]>([]);
  const [scopes, setScopes] = useState<string[]>(['business.read']);
  const [codeConfirmed, setCodeConfirmed] = useState(false);
  const [label, setLabel] = useState('Mi asistente');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');
  const enabled = process.env.NEXT_PUBLIC_QRCLIMA_ASSISTANT_ENABLED === 'true';

  useEffect(() => { setRequestId(new URLSearchParams(window.location.search).get('request') || ''); }, []);
  useEffect(() => {
    let current = true;
    setState(null); setDone(false); setCodeConfirmed(false); setScopes(['business.read']);
    if (!user || !organizationId || !enabled) return;
    Promise.all([
      assistantRequest<AssistantState>({ action: 'preview', organizationId }),
      assistantRequest<{ connections: AssistantConnection[] }>({ action: 'connections', organizationId }),
    ]).then(([preview, list]) => { if (current) { setState(preview); setConnections(list.connections); setError(''); } })
      .catch(err => { if (current) setError(err.message); });
    return () => { current = false; };
  }, [user, organizationId, enabled]);

  async function signIn(google = false) {
    setBusy(true); setError('');
    try {
      const result = google ? await loginWithGoogle() : await login(user?.email || email, password);
      setPassword(''); if (!result.success) setError(result.error || 'No se pudo iniciar sesión.');
    } finally { setBusy(false); }
  }
  async function approve() {
    if (!state || !codeConfirmed || !/^[a-f0-9]{64}$/.test(requestId)) return;
    setBusy(true); setError('');
    try {
      await assistantRequest({ action: 'approve', organizationId: state.organizationId, requestId, scopes, label });
      setDone(true);
    } catch (err) { setError(err instanceof Error ? err.message : 'No se completó la autorización.'); }
    finally { setBusy(false); }
  }
  async function revoke(id: string) {
    setBusy(true); setError('');
    try {
      await assistantRequest({ action:'revoke', organizationId, requestId:id });
      setConnections(previous => previous.map(c => c.id === id ? { ...c, revoked:true } : c));
    } catch (err) { setError(err instanceof Error ? err.message : 'No se pudo revocar.'); }
    finally { setBusy(false); }
  }

  return <main className="mx-auto max-w-xl px-5 py-12 text-slate-800">
    <div className="mb-6 text-sm font-semibold tracking-wide text-teal-700">QRclima · Mi asistente</div>
    <h1 className="text-3xl font-bold">Conecta tu asistente</h1>
    <p className="mt-3 text-slate-600">Elige qué puede hacer con los datos de tu organización. Puedes quitarle el acceso en esta página.</p>
    {!enabled ? <p role="status" className="mt-6 rounded-xl bg-amber-50 p-5">La herramienta está en preparación. Continúa utilizando el portal.</p>
      : loading ? <p role="status" className="mt-6">Comprobando tu cuenta…</p>
      : <>
        {!user && <section className="mt-6 rounded-2xl border bg-white p-6">
          <h2 className="text-lg font-semibold">Inicia sesión en QRclima</h2>
          <p className="mb-4 mt-2 text-sm text-slate-600">Tu contraseña se introduce aquí; no la compartas en el chat del asistente.</p>
          <form onSubmit={e => { e.preventDefault(); void signIn(); }} className="space-y-3">
            <label className="block text-sm">Correo<input type="email" required autoComplete="username" value={email} onChange={e => setEmail(e.target.value)} className="mt-1 w-full rounded-lg border p-3" /></label>
            <label className="block text-sm">Contraseña<input type="password" required autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} className="mt-1 w-full rounded-lg border p-3" /></label>
            <button disabled={busy} className="w-full rounded-lg bg-teal-700 p-3 font-semibold text-white disabled:opacity-50">Iniciar sesión</button>
          </form>
          <button onClick={() => void signIn(true)} disabled={busy} className="mt-3 w-full rounded-lg border p-3 disabled:opacity-50">Continuar con Google</button>
        </section>}
        {user && <section className="mt-6 rounded-2xl border bg-white p-6">
          <p className="text-sm text-slate-600">Cuenta: {user.email}</p>
          <label className="mt-4 block font-medium">Organización
            <select value={organizationId || ''} disabled={busy} className="mt-2 w-full rounded-lg border p-3" onChange={async e => {
              setBusy(true); const result = await switchOrg(e.target.value); if (!result.success) setError(result.error || 'No se pudo cambiar de organización.'); setBusy(false);
            }}>
              {Object.entries(memberships).map(([id, member]) => <option key={id} value={id}>{member.orgName || id}</option>)}
              {organizationId && !memberships[organizationId] && <option value={organizationId}>{state?.organization.name || organizationId}</option>}
            </select>
          </label>
          {done ? <p role="status" className="mt-5 rounded-lg bg-teal-50 p-4">Conexión autorizada. Vuelve a tu chat y escribe «continúa». El asistente comprobará el acceso.</p>
            : state && requestId && <>
              {!/^[a-f0-9]{64}$/.test(requestId) ? <p className="mt-4 text-red-700">Solicitud inválida. Vuelve a iniciar desde tu carpeta.</p> : <>
                <p className="mt-4">Código de esta conexión: <strong className="font-mono tracking-widest">{requestId.slice(0,8).toUpperCase()}</strong></p>
                <label className="mt-3 flex gap-3"><input type="checkbox" checked={codeConfirmed} onChange={e => setCodeConfirmed(e.target.checked)} />Este código coincide con el que veo en mi chat.</label>
                <label className="mt-4 block text-sm">Nombre para reconocer esta conexión<input maxLength={80} value={label} onChange={e => setLabel(e.target.value)} className="mt-1 w-full rounded-lg border p-3" /></label>
                <div className="mt-5 space-y-3">
                  <p className="font-medium">Permisos</p>
                  <p className="text-sm">Leer empresa, clientes, conceptos, citas, cotizaciones, ventas y documentos de esta organización.</p>
                  {permissions.filter(permission => permission.id !== 'branding.write' || state.owner).map(permission => <label key={permission.id} className="flex items-start gap-3 text-sm">
                    <input type="checkbox" checked={scopes.includes(permission.id)} onChange={e => setScopes(previous => e.target.checked ? [...previous,permission.id] : previous.filter(v => v !== permission.id))} />{permission.label}
                  </label>)}
                </div>
                <p className="mt-5 text-sm text-slate-600">El permiso caduca en 30 días. Los cambios requieren una petición concreta en el chat. La foto y el logo se muestran públicamente, igual que en QRclima; las constancias permanecen privadas. Los datos consultados pueden enviarse al proveedor de IA que elegiste.</p>
                <button onClick={() => void approve()} disabled={busy || !codeConfirmed || !label.trim()} className="mt-5 w-full rounded-lg bg-teal-700 p-3 font-semibold text-white disabled:opacity-50">Autorizar mi asistente</button>
              </>}
            </>}
          {error.includes('Vuelve a iniciar sesión aquí') && <div className="mt-4 space-y-3 rounded-xl bg-slate-50 p-4">
            <p className="text-sm">Verifica la sesión de {user.email} antes de autorizar.</p>
            <form onSubmit={e => { e.preventDefault(); void signIn(); }} className="flex gap-2">
              <label className="flex-1 text-sm">Contraseña<input type="password" required autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} className="mt-1 w-full rounded-lg border p-3" /></label>
              <button disabled={busy} className="self-end rounded-lg border p-3">Verificar</button>
            </form>
            <button disabled={busy} className="w-full rounded-lg border p-3" onClick={() => void signIn(true)}>Verificar con Google</button>
          </div>}
        </section>}
        {user && connections.length > 0 && <section className="mt-8">
          <h2 className="text-lg font-semibold">Mis conexiones</h2>
          <ul className="mt-3 space-y-3">{connections.map(connection => <li key={connection.id} className="flex items-center justify-between gap-3 rounded-xl border bg-white p-4">
            <div><p className="font-medium">{connection.label}</p><p className="text-xs text-slate-500">{connection.revoked ? 'Revocada' : 'Caduca ' + new Date(connection.expiresAt).toLocaleDateString('es-MX')}</p></div>
            {!connection.revoked && <button disabled={busy} onClick={() => void revoke(connection.id)} className="rounded-lg border px-3 py-2 text-sm disabled:opacity-50">Revocar</button>}
          </li>)}</ul>
        </section>}
      </>}
    {error && <p role="alert" className="mt-5 rounded-xl bg-red-50 p-4 text-red-800">{error}</p>}
  </main>;
}
