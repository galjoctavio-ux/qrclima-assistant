"""QRclima user connector. Python 3.10+, no Firebase/Admin SDK on the user's PC."""
import argparse
import base64
import ctypes
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
import uuid
import importlib.util

PORTAL = "https://app.tesivil.com/qrclima"
MAX_RESPONSE = 12 * 1024 * 1024
MESSAGES = {
    "unavailable": "El conector todavía no está habilitado en QRclima. Puedes continuar por el portal.",
    "unauthenticated": "La conexión está pendiente, expiró o fue revocada. Revisa la autorización en el navegador.",
    "permission_denied": "La cuenta, organización o permiso no permite esta operación.",
    "conflict": "Los datos cambiaron. Relee el estado y revisa el borrador antes de continuar.",
    "confirmation_required": "Falta confirmar los cambios o el archivo concreto.",
    "outcome_unknown": "La subida anterior necesita revisión. No repitas con otro identificador.",
    "resource_exhausted": "Se alcanzó un límite. Intenta más tarde.",
    "invalid_argument": "La solicitud contiene campos o un archivo no permitidos.",
}

class ConnectorError(ValueError):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ConnectorError("La conexión rechazó una redirección inesperada.")

def endpoint(value):
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port not in (None, 443) or parsed.query or parsed.fragment:
        raise ConnectorError("El conector necesita una dirección HTTPS válida.")
    if not parsed.hostname or not (parsed.hostname.endswith(".cloudfunctions.net") or parsed.hostname.endswith(".run.app")):
        raise ConnectorError("El servidor no pertenece a la infraestructura autorizada de QRclima.")
    return value

def request(url, payload=None, credential=None):
    headers = {"Accept": "application/json"}
    if credential:
        headers["Authorization"] = " ".join(("Bearer", credential))
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(req, timeout=45) as response:
            body = response.read(MAX_RESPONSE + 1)
        if len(body) > MAX_RESPONSE:
            raise ConnectorError("La respuesta supera el límite permitido.")
        return json.loads(body)
    except urllib.error.HTTPError as exc:
        try:
            code = json.loads(exc.read(4096)).get("error", {}).get("code", "unavailable")
        except (ValueError, AttributeError):
            code = "unavailable"
        error = ConnectorError(MESSAGES.get(code, "No se completó la operación. Comprueba su estado antes de repetir."))
        error.code = code
        raise error from None
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        if isinstance(exc, ConnectorError):
            raise
        raise ConnectorError("No se pudo conectar. Revisa internet y el estado de QRclima; comprueba una escritura antes de repetirla.") from None

def root_path(value):
    root = Path(value).absolute()
    def linked(path):
        return path.exists() and (path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400))
    if linked(root) or any(linked(parent) for parent in root.parents):
        raise ConnectorError("La carpeta privada no puede ser un enlace.")
    if ".agents" in root.parts or "public" in root.parts:
        raise ConnectorError("Usa una carpeta privada fuera de las fuentes públicas.")
    root.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        os.chmod(root, 0o700)
    return root

def protect(content, decrypt=False):
    if os.name != "nt":
        return content
    from ctypes import wintypes
    class Blob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]
    memory = ctypes.create_string_buffer(content)
    source = Blob(len(content), ctypes.cast(memory, ctypes.POINTER(ctypes.c_ubyte)))
    result = Blob()
    crypt = ctypes.windll.crypt32
    method = crypt.CryptUnprotectData if decrypt else crypt.CryptProtectData
    method.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    method.restype = wintypes.BOOL
    local_free = ctypes.windll.kernel32.LocalFree
    local_free.argtypes = [ctypes.c_void_p]
    local_free.restype = ctypes.c_void_p
    if not method(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(result)):
        raise ConnectorError("Windows no pudo proteger la conexión para este usuario.")
    try:
        return ctypes.string_at(result.pbData, result.cbData)
    finally:
        local_free(result.pbData)

def session_path(root):
    return root / ("connection.dpapi" if os.name == "nt" else "connection.json")

def save_session(root, session):
    path = session_path(root)
    if path.exists() or path.is_symlink():
        raise ConnectorError("Ya hay una conexión o solicitud. Consulta status o desconecta antes de crear otra.")
    data = protect(json.dumps(session).encode("utf-8"))
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(data)
        output.flush()
        os.fsync(output.fileno())

def load_session(root):
    path = session_path(root)
    if path.is_symlink() or not path.is_file():
        raise ConnectorError("Falta la conexión. Ejecuta inicia.")
    if os.name != "nt" and stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise ConnectorError("La conexión tiene permisos demasiado amplios; restringe el archivo a su dueño.")
    if path.stat().st_size > 16000:
        raise ConnectorError("Archivo de conexión inválido.")
    try:
        session = json.loads(protect(path.read_bytes(), decrypt=True))
        endpoint(session["api"])
        if not isinstance(session["credential"], str) or len(session["credential"]) != 43:
            raise ValueError()
        return session
    except (ValueError, KeyError, UnicodeError):
        raise ConnectorError("No se pudo leer la conexión privada de este usuario.") from None

def initiate(root, open_browser=True):
    config = request(PORTAL + "/assistant/connector-config")
    if config.get("enabled") is not True:
        raise ConnectorError(MESSAGES["unavailable"])
    api = endpoint(config.get("api", ""))
    credential = secrets.token_urlsafe(32)
    request_id = hashlib.sha256(credential.encode("ascii")).hexdigest()
    save_session(root, {"api": api, "credential": credential, "createdAt": time.time()})
    url = PORTAL + "/assistant/connect?request=" + request_id
    if open_browser:
        webbrowser.open(url)
    return {"state": "awaiting_browser", "url": url, "code": request_id[:8].upper(),
            "instruction": "Inicia sesión tú mismo, comprueba el código y autoriza tu organización. Después ejecuta status."}

def call(root, body):
    session = load_session(root)
    response = request(session["api"], body, session["credential"])
    if "result" not in response:
        raise ConnectorError("QRclima devolvió una respuesta incompleta.")
    return response["result"]

def stores():
    modules = []
    for name in ("profile_store", "context_store"):
        spec = importlib.util.spec_from_file_location("qrclima_connector_" + name, Path(__file__).with_name(name + ".py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules.append(module)
    return modules

def sync_identity(root, profile_id, state):
    store, _ = stores()
    path = store.profile_path(root, profile_id)
    if not path.exists():
        store.init_profile(root, profile_id)
    profile = store.load_profile(path, profile_id)
    previous = profile["qrclima"]["account_uid"]
    if previous["value"] is not None and previous["value"] != state["uid"]:
        raise ConnectorError("Este perfil pertenece a otra cuenta. Usa una carpeta o un perfil nuevo; no mezcles sus datos.")
    stamp = store.now()
    def verified(value):
        return {"value": value, "status": "verified", "source": {"type": "authorized_connector", "reference": "QRclima assistant status"},
                "observed_at": stamp, "verified_at": stamp}
    org_id = state["organizationId"]
    orgs = [org for org in profile["qrclima"]["organizations"] if org["id"]["value"] != org_id]
    orgs.append({"id": verified(org_id), "name": verified(state["organization"].get("name")),
                 "plan": verified(state["organization"].get("plan")), "membership_role": verified("owner" if state["owner"] else "admin"),
                 "membership_active": verified(True)})
    changes = [{"path": "/qrclima/account_uid", "value": verified(state["uid"])},
               {"path": "/qrclima/active_organization_id", "value": org_id}, {"path": "/qrclima/organizations", "value": orgs}]
    store.apply_patch(root, profile_id, profile["revision"], {"changes": changes})
    return state

def synchronize(root, profile_id, max_pages=3):
    if max_pages < 1 or max_pages > 10:
        raise ConnectorError("La carga admite entre 1 y 10 páginas por categoría.")
    state = sync_identity(root, profile_id, call(root, {"action": "status"}))
    store, context = stores()
    mapping = {"clients": "clients", "concepts": "concepts", "pro_concepts": "concepts", "appointments": "appointments",
               "quotes": "quotations", "pro_quotes": "quotations", "documents": "documents"}
    results = []
    for category, target in mapping.items():
        cursor, count = None, 0
        for _ in range(max_pages):
            page = call(root, {"action": "read", "category": category, "limit": 100, "cursor": cursor})
            if page.get("organizationId") != state["organizationId"]:
                raise ConnectorError("La lectura no coincide con la organización de esta conexión.")
            reference = "QRclima assistant read " + category
            # Each page is partial; no page certifies the complete company's dataset.
            snapshot = {"schema_version": "0.1.0", "snapshot_id": "connector-" + uuid.uuid4().hex,
                "profile_id": profile_id, "organization_id": state["organizationId"], "actor_uid": state["uid"], "account_reference": None,
                "category": target, "observed_at": store.now(), "source": {"type": "authorized_connector", "reference": reference},
                "coverage": {"state": "partial", "scope": category + "; página de la colección autorizada", "next_cursor": page["nextCursor"]},
                "records": [{"record_id": category + ":" + record["id"], "data": record, "evidence_refs": [reference]} for record in page["records"]]}
            directory = context.context_directory(store.profile_path(root, profile_id), state["organizationId"])
            index = context.load_index(directory, profile_id, state["organizationId"])
            context.put_snapshot(root, profile_id, index["revision"], snapshot)
            count += len(page["records"])
            cursor = page["nextCursor"]
            if not cursor:
                break
        results.append({"category": category, "cached": count, "nextCursor": cursor, "scope": "colección del conector"})
    return {"organizationId": state["organizationId"], "categories": results,
            "notice": "Contexto privado observado. Documents incluye constancias guardadas por el conector; los demás PDFs se consultan en el portal. Relee antes de operar."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Carpeta privada .qrclima de este proyecto")
    parser.add_argument("--profile", default="principal")
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("inicia")
    start.add_argument("--no-browser", action="store_true")
    sub.add_parser("status")
    sync = sub.add_parser("sync")
    sync.add_argument("--max-pages", type=int, default=3)
    read = sub.add_parser("read")
    read.add_argument("category", choices=["clients", "appointments", "concepts", "pro_concepts", "quotes", "pro_quotes", "sales", "documents"])
    read.add_argument("--cursor")
    read.add_argument("--limit", type=int, default=50)
    update = sub.add_parser("update")
    update.add_argument("target", choices=["profile", "branding"])
    update.add_argument("--input", required=True, help="JSON privado con patch, expectedRevision, requestId y confirmed")
    upload = sub.add_parser("upload")
    upload.add_argument("kind", choices=["profile_photo", "organization_logo", "constancia"])
    upload.add_argument("--file", required=True)
    upload.add_argument("--request-id", required=True)
    upload.add_argument("--revision")
    upload.add_argument("--confirmed", action="store_true")
    download = sub.add_parser("download")
    download.add_argument("document_id")
    download.add_argument("--output", required=True)
    sub.add_parser("disconnect")
    sub.add_parser("cancel-pending")
    args = parser.parse_args()
    try:
        root = root_path(args.root)
        if args.command == "inicia":
            result = initiate(root, not args.no_browser)
        elif args.command == "cancel-pending":
            session = load_session(root)
            # A valid connection must be revoked on the server before removing its key.
            try:
                request(session["api"], {"action": "status"}, session["credential"])
            except ConnectorError as exc:
                if getattr(exc, "code", None) != "unauthenticated":
                    raise
            else:
                raise ConnectorError("La conexión está activa. Utiliza disconnect para revocarla.")
            session_path(root).unlink()
            result = {"cancelled": True}
        elif args.command == "status":
            result = sync_identity(root, args.profile, call(root, {"action": "status"}))
        elif args.command == "sync":
            result = synchronize(root, args.profile, args.max_pages)
        elif args.command == "read":
            result = call(root, {"action": "read", "category": args.category, "limit": args.limit, "cursor": args.cursor})
        elif args.command == "update":
            content = Path(args.input).read_bytes()
            if len(content) > 16000:
                raise ConnectorError("Borrador demasiado grande.")
            body = json.loads(content)
            if not isinstance(body, dict) or set(body) != {"patch", "expectedRevision", "requestId", "confirmed"}:
                raise ConnectorError("El borrador necesita patch, expectedRevision, requestId y confirmed.")
            result = call(root, {**body, "action": "update_" + args.target})
        elif args.command == "upload":
            path = Path(args.file)
            cap = {"profile_photo": 5, "organization_logo": 2, "constancia": 8}[args.kind] * 1024 * 1024
            if path.is_symlink() or not path.is_file() or path.stat().st_size > cap:
                raise ConnectorError("Archivo inexistente, enlazado o demasiado grande.")
            result = call(root, {"action": "upload", "kind": args.kind, "name": path.name,
                "contentBase64": base64.b64encode(path.read_bytes()).decode("ascii"), "requestId": args.request_id,
                "expectedRevision": args.revision, "confirmed": args.confirmed})
        elif args.command == "download":
            result = call(root, {"action": "download", "documentId": args.document_id})
            output = Path(args.output).absolute()
            if not output.is_relative_to(root.resolve()) or output.is_symlink():
                raise ConnectorError("Guarda el documento dentro de la carpeta privada.")
            output.parent.mkdir(parents=True, exist_ok=True)
            if not output.resolve().is_relative_to(root.resolve()):
                raise ConnectorError("El destino sale de la carpeta privada.")
            with output.open("xb") as file:
                file.write(base64.b64decode(result.pop("contentBase64"), validate=True))
            if os.name != "nt":
                os.chmod(output, 0o600)
            result["savedLocally"] = str(output)
        else:
            result = call(root, {"action": "disconnect"})
            session_path(root).unlink()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ConnectorError, OSError, ValueError) as exc:
        message = str(exc) if isinstance(exc, ConnectorError) else "No se completó la operación; revisa archivo y formato."
        parser.exit(2, message + "\n")

if __name__ == "__main__":
    main()
