"""Local QRclima profiles. No network, service authentication or business writes."""
import argparse
import copy
import json
import math
import os
import re
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

PUBLIC_ROOT = Path(__file__).resolve().parents[1]
RESERVED = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
SECRET_KEYS = {"password", "passwd", "secret", "api_key", "apikey", "access_token", "refresh_token", "private_key", "client_secret", "authorization_header"}
SECRET_PATTERN = re.compile(r"\bsk-[A-Za-z0-9_-]{12,}|\bBearer\s+\S+|-----BEGIN [A-Z ]*PRIVATE KEY-----|\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", re.I)


class ProfileError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ProfileError("No se pudo leer el archivo JSON; revisa ruta y formato.") from exc


def reject_secrets(value):
    if isinstance(value, dict):
        if any(str(key).lower() in SECRET_KEYS for key in value):
            raise ProfileError("El archivo contiene un campo de credencial; usa una referencia externa.")
        for child in value.values():
            reject_secrets(child)
    elif isinstance(value, list):
        for child in value:
            reject_secrets(child)
    elif isinstance(value, str) and SECRET_PATTERN.search(value):
        raise ProfileError("Se detecto un formato de secreto; no se guardo ni imprimio su valor.")


def validate_schema(value, rule, schema=None, path="/"):
    """Validate the JSON Schema subset used by this package, without dependencies."""
    schema = schema or rule
    if "$ref" in rule:
        reference = rule["$ref"]
        if not reference.startswith("#/"):
            raise ProfileError("El validador no carga esquemas remotos.")
        target = schema
        for part in reference[2:].split("/"):
            target = target[part]
        return validate_schema(value, target, schema, path)
    types = {"object": dict, "array": list, "string": str, "boolean": bool, "integer": int, "number": (int, float), "null": type(None)}
    requested = rule.get("type")
    if requested:
        allowed = requested if isinstance(requested, list) else [requested]
        matches = any(isinstance(value, types[t]) and not (t in {"integer", "number"} and isinstance(value, bool)) for t in allowed)
        if not matches:
            raise ProfileError(f"Tipo invalido en {path}.")
    if "const" in rule and value != rule["const"]:
        raise ProfileError(f"Valor fijo invalido en {path}.")
    if "enum" in rule and value not in rule["enum"]:
        raise ProfileError(f"Opcion invalida en {path}.")
    if isinstance(value, dict):
        if any(key not in value for key in rule.get("required", [])):
            raise ProfileError(f"Faltan campos requeridos en {path}.")
        properties = rule.get("properties", {})
        if rule.get("additionalProperties") is False and set(value) - set(properties):
            raise ProfileError(f"Hay campos no permitidos en {path}.")
        for key, child in value.items():
            if key in properties:
                validate_schema(child, properties[key], schema, path.rstrip("/") + "/" + key)
    if isinstance(value, list):
        if len(value) < rule.get("minItems", 0):
            raise ProfileError(f"Lista incompleta en {path}.")
        if len(value) > rule.get("maxItems", 10**9):
            raise ProfileError(f"Lista demasiado extensa en {path}.")
        for i, child in enumerate(value):
            validate_schema(child, rule.get("items", {}), schema, path.rstrip("/") + f"/{i}")
    if isinstance(value, str):
        if not rule.get("minLength", 0) <= len(value) <= rule.get("maxLength", 10**9):
            raise ProfileError(f"Longitud invalida en {path}.")
        if "pattern" in rule and not re.search(rule["pattern"], value):
            raise ProfileError(f"Formato invalido en {path}.")
        if rule.get("format") == "date-time":
            try:
                if "T" not in value or datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is None:
                    raise ValueError()
            except ValueError as exc:
                raise ProfileError(f"Fecha sin formato o zona valida en {path}.") from exc
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value) or value < rule.get("minimum", -math.inf):
            raise ProfileError(f"Numero invalido en {path}.")


def fact():
    return {"value": None, "status": "unknown", "source": None, "observed_at": None, "verified_at": None}


def new_profile(profile_id):
    timestamp = now()
    return {
        "schema_version": "0.1.0", "profile_id": profile_id, "revision": 0, "created_at": timestamp, "updated_at": timestamp,
        "person": {name: fact() for name in ("display_name", "language", "time_zone")},
        "paths": {name: fact() for name in ("documents_directory", "receipts_directory")},
        "qrclima": {"portal_url": "https://app.tesivil.com/qrclima", "account_uid": fact(), "account_reference": fact(), "active_organization_id": None, "organizations": []},
        "connections": {"operating_system": fact(), "browser": {"provider": fact(), "state": "unknown", "checked_at": None}, "vm": {name: fact() for name in ("used", "host", "provider", "purpose", "credential_reference")}, "whatsapp": {"mode": "disabled"}, "sdk": {"mode": "disabled"}},
        "operation_policy": {"sales": "draft_only", "agenda": "draft_only", "finance": "read_only", "external_messages": "disabled", "sdk_writes": "disabled"},
        "policy_history": [], "authorizations": [], "learning_proposals": [],
        "preferences": [{"key": key, "organization_id": None, "setting": fact()} for key in ("response-style", "preferred-browser", "documents-naming", "appointment-duration-minutes", "quotation-footer")],
        "improvement_proposals": [],
    }


def validate_profile(profile):
    reject_secrets(profile)
    validate_schema(profile, read_json(PUBLIC_ROOT / "schemas/profile.schema.json"))
    if profile["profile_id"] in RESERVED:
        raise ProfileError("Alias reservado por el sistema operativo.")
    def check_facts(value, path=""):
        if isinstance(value, dict):
            if set(value) == {"value", "status", "source", "observed_at", "verified_at"}:
                status = value["status"]
                if status == "unknown" and any(value[k] is not None for k in ("value", "source", "observed_at", "verified_at")):
                    raise ProfileError("Un dato desconocido debe mantener valor y evidencia nulos.")
                if status != "unknown" and (value["value"] is None or value["source"] is None or value["observed_at"] is None):
                    raise ProfileError("Un dato conocido necesita valor, fuente y fecha.")
                if status == "verified":
                    if value["verified_at"] is None or value["source"]["type"] == "user":
                        raise ProfileError("Una declaracion del usuario no equivale a verificacion.")
                    if path.startswith("/qrclima/") and value["source"]["type"] not in {"qrclima_ui", "authorized_connector"}:
                        raise ProfileError("La identidad de QRclima debe verificarse en una fuente autorizada.")
                if status in {"unknown", "declared"} and value["verified_at"] is not None:
                    raise ProfileError("El estado declarado no puede tener una verificacion.")
            for key, child in value.items():
                check_facts(child, path + "/" + key)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                check_facts(child, path + f"/{i}")
    check_facts(profile)
    string_facts = [*profile["person"].values(), *profile["paths"].values(), profile["qrclima"]["account_uid"], profile["connections"]["operating_system"], profile["connections"]["browser"]["provider"]]
    string_facts += [value for key, value in profile["connections"]["vm"].items() if key != "used"]
    if "account_reference" in profile["qrclima"]:
        string_facts.append(profile["qrclima"]["account_reference"])
    identifiers = []
    for org in profile["qrclima"]["organizations"]:
        string_facts += [org[name] for name in ("id", "name", "plan", "membership_role")]
        if org["membership_active"]["value"] is not None and not isinstance(org["membership_active"]["value"], bool):
            raise ProfileError("El estado de membresia debe ser booleano.")
        if org["id"]["value"] is not None:
            identifiers.append(org["id"]["value"])
    if any(f["value"] is not None and (not isinstance(f["value"], str) or not f["value"].strip()) for f in string_facts):
        raise ProfileError("Un campo de texto contiene un valor invalido.")
    if len(set(identifiers)) != len(identifiers):
        raise ProfileError("La organizacion ya existe en el perfil.")
    active = profile["qrclima"]["active_organization_id"]
    if active is not None and active not in identifiers:
        raise ProfileError("La organizacion activa no esta registrada en este perfil.")
    preference_keys = set()
    for preference in profile.get("preferences", []):
        scope = (preference["key"], preference["organization_id"])
        if scope in preference_keys:
            raise ProfileError("La preferencia ya existe en ese alcance.")
        preference_keys.add(scope)
        if preference["organization_id"] is not None and preference["organization_id"] not in identifiers:
            raise ProfileError("La preferencia pertenece a una organizacion no registrada.")
    proposal_ids = [item["id"] for item in profile.get("improvement_proposals", [])]
    if len(set(proposal_ids)) != len(proposal_ids):
        raise ProfileError("La propuesta de mejora ya existe en el perfil.")
    used = profile["connections"]["vm"]["used"]["value"]
    if used is not None and not isinstance(used, bool):
        raise ProfileError("El uso de VM debe ser booleano.")
    browser = profile["connections"]["browser"]
    if browser["state"] != "unknown" and browser["checked_at"] is None:
        raise ProfileError("El estado de navegador necesita fecha de comprobacion.")


def validate_operation(operation):
    reject_secrets(operation)
    validate_schema(operation, read_json(PUBLIC_ROOT / "schemas/operation.schema.json"))
    if operation["state"] in {"executing", "outcome_unknown", "verified"}:
        if not operation["organization_id"] or not (operation["actor_uid"] or operation.get("actor_reference")):
            raise ProfileError("La operacion requiere organizacion y actor identificados.")
        if operation["kind"] != "finance_read" and not operation["authorization_ref"]:
            raise ProfileError("La escritura requiere referencia de autorizacion.")
    if operation["state"] == "verified" and (operation["result"] is None or operation["missing_fields"]):
        raise ProfileError("Un resultado verificado necesita registro, relectura y datos completos.")


def profile_path(root, profile_id):
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", profile_id) or profile_id in RESERVED:
        raise ProfileError("Alias invalido; usa letras minusculas, numeros y guiones.")
    workspace_root = PUBLIC_ROOT.parent / ".qrclima" if PUBLIC_ROOT.name == ".agents" and (PUBLIC_ROOT.parent / "AGENTS.md").is_file() else None
    root = Path(root or os.environ.get("QRCLIMA_AGENT_HOME") or os.environ.get("PLUGIN_DATA") or workspace_root or Path.home() / ".qrclima-agent").expanduser().resolve()
    if root == PUBLIC_ROOT or PUBLIC_ROOT in root.parents:
        raise ProfileError("Los datos privados no se guardan dentro del paquete publico.")
    target = (root / "profiles" / profile_id / "profile.json").resolve()
    if not target.is_relative_to(root):
        raise ProfileError("La ruta del perfil sale de su directorio privado.")
    return target


def load_profile(path, profile_id):
    data = read_json(path)
    validate_profile(data)
    if data["profile_id"] != profile_id:
        raise ProfileError("El archivo pertenece a otro perfil.")
    # The new optional account reference starts unknown for existing 0.1 profiles.
    data["qrclima"].setdefault("account_reference", fact())
    data.setdefault("preferences", new_profile(profile_id)["preferences"])
    data.setdefault("improvement_proposals", [])
    return data


@contextmanager
def profile_lock(directory):
    lock = directory / ".write-lock"
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise ProfileError("Otro proceso tiene el bloqueo; relee y reintenta cuando termine.") from exc
    try:
        yield
    finally:
        lock.rmdir()


def commit(path, data, fields):
    validate_profile(data)
    event = {"event_id": str(uuid.uuid4()), "revision": data["revision"], "fields": fields, "timestamp": now()}
    journal = path.with_name("journal.jsonl")
    with journal.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({**event, "state": "prepared"}, ensure_ascii=False) + "\n")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    try:
        with journal.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({**event, "state": "committed"}, ensure_ascii=False) + "\n")
    except OSError as exc:
        raise ProfileError(f"Perfil guardado en revision {data['revision']}; diario incompleto. Relee antes de reintentar.") from exc


def init_profile(root, profile_id):
    path = profile_path(root, profile_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with profile_lock(path.parent):
        if path.exists():
            raise ProfileError("El perfil ya existe; no se sobreescribio.")
        (path.parent / "receipts").mkdir(exist_ok=True)
        commit(path, new_profile(profile_id), ["initial_profile"])
    return path


def apply_patch(root, profile_id, expected_revision, patch):
    path = profile_path(root, profile_id)
    reject_secrets(patch)
    if not isinstance(patch, dict) or set(patch) != {"changes"} or not isinstance(patch["changes"], list) or not patch["changes"]:
        raise ProfileError("El patch necesita una lista no vacia de cambios.")
    with profile_lock(path.parent):
        data = load_profile(path, profile_id)
        if data["revision"] != expected_revision:
            raise ProfileError("Conflicto de revision; relee y reconcilia los cambios.")
        result = copy.deepcopy(data)
        changed = []
        for change in patch["changes"]:
            if not isinstance(change, dict) or set(change) != {"path", "value"} or not isinstance(change["path"], str):
                raise ProfileError("Cada cambio requiere path y value.")
            pointer = change["path"]
            if not pointer.startswith("/"):
                raise ProfileError("El path debe ser un JSON Pointer absoluto.")
            parts = [p.replace("~1", "/").replace("~0", "~") for p in pointer[1:].split("/")]
            if parts[0] not in {"person", "paths", "qrclima", "connections", "learning_proposals", "preferences", "improvement_proposals"}:
                raise ProfileError("Ese campo no se actualiza mediante el patch de configuracion.")
            target = result
            for part in parts[:-1]:
                if not isinstance(target, dict) or part not in target:
                    raise ProfileError("El path no corresponde a un campo de configuracion.")
                target = target[part]
            if not isinstance(target, dict) or parts[-1] not in target:
                raise ProfileError("El path no corresponde a un campo de configuracion.")
            target[parts[-1]] = copy.deepcopy(change["value"])
            changed.append(pointer)
        result["revision"] += 1
        result["updated_at"] = now()
        commit(path, result, changed)
    return result["revision"]


def set_mode(root, profile_id, expected_revision, capability, mode, evidence_ref):
    if capability not in {"sales", "agenda"} or mode not in {"draft_only", "confirm_each"} or not evidence_ref.strip():
        raise ProfileError("Capacidad, modo o referencia de instruccion invalida.")
    path = profile_path(root, profile_id)
    with profile_lock(path.parent):
        data = load_profile(path, profile_id)
        if data["revision"] != expected_revision:
            raise ProfileError("Conflicto de revision; relee y reconcilia los cambios.")
        data["operation_policy"][capability] = mode
        data["policy_history"].append({"capability": capability, "mode": mode, "evidence_ref": evidence_ref, "changed_at": now()})
        data["revision"] += 1
        data["updated_at"] = now()
        commit(path, data, [f"/operation_policy/{capability}", "/policy_history"])
    return data["revision"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "summary", "validate", "apply", "set-mode"):
        item = sub.add_parser(name)
        item.add_argument("--root")
        item.add_argument("--profile", required=True)
        if name in {"apply", "set-mode"}:
            item.add_argument("--expected-revision", type=int, required=True)
        if name == "apply":
            item.add_argument("--patch", required=True)
        if name == "set-mode":
            item.add_argument("--capability", choices=("sales", "agenda"), required=True)
            item.add_argument("--mode", choices=("draft_only", "confirm_each"), required=True)
            item.add_argument("--evidence-ref", required=True)
    item = sub.add_parser("validate-operation")
    item.add_argument("--file", required=True)
    args = parser.parse_args()
    try:
        if args.command == "validate-operation":
            validate_operation(read_json(args.file))
            print("Contrato de operacion valido; no prueba ejecucion real.")
            return
        if args.command == "init":
            print(f"Perfil creado: {init_profile(args.root, args.profile)}")
            return
        if args.command == "apply":
            revision = apply_patch(args.root, args.profile, args.expected_revision, read_json(args.patch))
            print(f"Perfil actualizado; revision {revision}.")
            return
        if args.command == "set-mode":
            revision = set_mode(args.root, args.profile, args.expected_revision, args.capability, args.mode, args.evidence_ref)
            print(f"Modo actualizado; revision {revision}. Los permisos reales se comprueban en QRclima.")
            return
        path = profile_path(args.root, args.profile)
        data = load_profile(path, args.profile)
        if args.command == "validate":
            print(f"Perfil valido; revision {data['revision']}. Las fuentes no se autentican con este validador.")
        else:
            print(json.dumps({"profile_id": data["profile_id"], "revision": data["revision"], "private_path": str(path), "display_name": data["person"]["display_name"], "time_zone": data["person"]["time_zone"], "active_organization_id": data["qrclima"]["active_organization_id"], "browser_state": data["connections"]["browser"]["state"], "modes": data["operation_policy"]}, indent=2, ensure_ascii=False))
    except (ProfileError, OSError) as exc:
        # OSError filenames may contain personal data; do not echo raw system errors.
        parser.exit(2, (str(exc) if isinstance(exc, ProfileError) else "Error local de archivos; revisa permisos y existencia.") + "\n")


if __name__ == "__main__":
    main()
