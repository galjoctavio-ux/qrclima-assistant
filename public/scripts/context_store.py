"""Private organization snapshots. Local files only; does not connect to QRclima."""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path

RESOURCE_ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("qrclima_profile_store", RESOURCE_ROOT / "scripts/profile_store.py")
store = importlib.util.module_from_spec(spec)
spec.loader.exec_module(store)
CATEGORIES = ("company", "clients", "concepts", "appointments", "quotations", "documents")


def validate_snapshot(snapshot):
    store.reject_secrets(snapshot)
    store.validate_schema(snapshot, store.read_json(RESOURCE_ROOT / "schemas/context-snapshot.schema.json"))
    if not snapshot["actor_uid"] and not snapshot["account_reference"]:
        raise store.ProfileError("El snapshot necesita una referencia de cuenta o UID comprobado.")
    ids = [record["record_id"] for record in snapshot["records"]]
    if len(set(ids)) != len(ids):
        raise store.ProfileError("Hay registros repetidos dentro del snapshot.")
    if snapshot["coverage"]["state"] == "unavailable" and snapshot["records"]:
        raise store.ProfileError("Una categoria inaccesible no contiene registros observados.")
    if snapshot["coverage"]["state"] == "complete" and snapshot["coverage"]["next_cursor"]:
        raise store.ProfileError("Una cobertura completa no puede tener una pagina pendiente.")


def organization_context(profile, snapshot=None):
    org_id = profile["qrclima"]["active_organization_id"]
    org = next((item for item in profile["qrclima"]["organizations"] if item["id"]["value"] == org_id), None)
    if not org_id or org is None or org["id"]["status"] != "verified":
        raise store.ProfileError("Falta una organizacion activa comprobada para guardar o consultar el indice.")
    if snapshot is not None:
        if snapshot["profile_id"] != profile["profile_id"] or snapshot["organization_id"] != org_id:
            raise store.ProfileError("El snapshot no corresponde al perfil y organizacion activos.")
        for snapshot_field, profile_field in (("actor_uid", "account_uid"), ("account_reference", "account_reference")):
            value = snapshot[snapshot_field]
            if value is not None:
                identifier = profile["qrclima"].get(profile_field, store.fact())
                if identifier["status"] != "verified" or identifier["value"] != value:
                    raise store.ProfileError("La cuenta del snapshot no coincide con una identidad comprobada del perfil.")
    return org_id


def context_directory(profile_path, org_id):
    base = (profile_path.parent / "context").resolve()
    target = (base / hashlib.sha256(org_id.encode("utf-8")).hexdigest()).resolve()
    if not base.is_relative_to(profile_path.parent.resolve()) or not target.is_relative_to(base):
        raise store.ProfileError("La ruta de contexto sale de su perfil privado.")
    return target


def load_index(directory, profile_id, org_id):
    path = directory / "index.json"
    if not path.exists():
        return {"schema_version": "0.1.0", "profile_id": profile_id, "organization_id": org_id, "revision": 0, "snapshots": []}
    data = store.read_json(path)
    store.reject_secrets(data)
    if not isinstance(data, dict) or data.get("profile_id") != profile_id or data.get("organization_id") != org_id:
        raise store.ProfileError("El indice pertenece a otro perfil u organizacion.")
    if type(data.get("revision")) is not int or data["revision"] < 0 or not isinstance(data.get("snapshots"), list):
        raise store.ProfileError("El indice local tiene un formato invalido.")
    if any(not isinstance(item, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", item) for item in data["snapshots"]):
        raise store.ProfileError("El indice contiene un ID de snapshot invalido.")
    return data


def put_snapshot(root, profile_id, expected_revision, snapshot):
    validate_snapshot(snapshot)
    profile_path = store.profile_path(root, profile_id)
    with store.profile_lock(profile_path.parent):
        profile = store.load_profile(profile_path, profile_id)
        org_id = organization_context(profile, snapshot)
        directory = context_directory(profile_path, org_id)
        directory.mkdir(parents=True, exist_ok=True)
        index = load_index(directory, profile_id, org_id)
        if index["revision"] != expected_revision:
            raise store.ProfileError("Conflicto de revision del contexto; relee antes de reintentar.")
        target = (directory / (snapshot["snapshot_id"] + ".json")).resolve()
        if not target.is_relative_to(directory):
            raise store.ProfileError("La ruta del snapshot sale del contexto privado.")
        if target.exists():
            raise store.ProfileError("El snapshot ya existe; no se reemplazo.")
        with target.open("x", encoding="utf-8") as stream:
            json.dump(snapshot, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        index["snapshots"].append(snapshot["snapshot_id"])
        index["revision"] += 1
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory, suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(index, stream, indent=2, ensure_ascii=False, allow_nan=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, directory / "index.json")
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
        return index["revision"]


def read_snapshots(root, profile_id):
    profile_path = store.profile_path(root, profile_id)
    # Lock also prevents a profile/organization switch during the local read.
    with store.profile_lock(profile_path.parent):
        profile = store.load_profile(profile_path, profile_id)
        org_id = organization_context(profile)
        directory = context_directory(profile_path, org_id)
        index = load_index(directory, profile_id, org_id)
        snapshots = []
        for identifier in index["snapshots"]:
            path = (directory / (identifier + ".json")).resolve()
            if not path.is_relative_to(directory):
                raise store.ProfileError("La ruta del snapshot sale del contexto privado.")
            snapshot = store.read_json(path)
            validate_snapshot(snapshot)
            organization_context(profile, snapshot)
            if snapshot["snapshot_id"] != identifier:
                raise store.ProfileError("El archivo no corresponde al ID de snapshot solicitado.")
            snapshots.append(snapshot)
        return index, snapshots


def context_status(root, profile_id):
    index, snapshots = read_snapshots(root, profile_id)
    return {"profile_id": profile_id, "organization_id": index["organization_id"], "revision": index["revision"], "snapshots": [{"snapshot_id": s["snapshot_id"], "category": s["category"], "observed_at": s["observed_at"], "coverage": s["coverage"], "records": len(s["records"])} for s in snapshots]}


def search_context(root, profile_id, category, term, limit=20):
    if category not in CATEGORIES or not 1 <= limit <= 200:
        raise store.ProfileError("Categoria o limite de busqueda invalido.")
    index, snapshots = read_snapshots(root, profile_id)
    records = {}
    selected = [s for s in snapshots if s["category"] == category]
    selected.sort(key=lambda s: datetime.fromisoformat(s["observed_at"].replace("Z", "+00:00")))
    for snapshot in selected:
        for record in snapshot["records"]:
            records[record["record_id"]] = {**record, "observed_at": snapshot["observed_at"], "source": snapshot["source"], "snapshot_id": snapshot["snapshot_id"]}
    matches = [record for record in records.values() if term.casefold() in json.dumps(record["data"], ensure_ascii=False).casefold()]
    return {"organization_id": index["organization_id"], "category": category, "matches_in_cache": len(matches), "truncated": len(matches) > limit, "records": matches[:limit], "notice": "Indice local observado; confirma estado actual en QRclima. Una busqueda vacia no prueba ausencia."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("status", "put", "search"):
        item = sub.add_parser(command)
        item.add_argument("--root")
        item.add_argument("--profile", required=True)
        if command == "put":
            item.add_argument("--file", required=True)
            item.add_argument("--expected-revision", required=True, type=int)
        if command == "search":
            item.add_argument("--category", required=True, choices=CATEGORIES)
            item.add_argument("--term", required=True)
            item.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    try:
        if args.command == "put":
            if Path(args.file).stat().st_size > 8 * 1024 * 1024:
                raise store.ProfileError("El snapshot supera 8 MiB; divide la lectura en etapas.")
            revision = put_snapshot(args.root, args.profile, args.expected_revision, store.read_json(args.file))
            print(f"Snapshot local guardado; revision de contexto {revision}. No autentica la fuente ni modifica QRclima.")
        else:
            result = context_status(args.root, args.profile) if args.command == "status" else search_context(args.root, args.profile, args.category, args.term, args.limit)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    except (store.ProfileError, OSError) as exc:
        parser.exit(2, (str(exc) if isinstance(exc, store.ProfileError) else "Error local de contexto; revisa archivos y permisos sin repetir una operacion comercial.") + "\n")


if __name__ == "__main__":
    main()
