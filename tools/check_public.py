"""Check allowlisted public sources, Git index and optional reachable history."""
import argparse
import importlib.util
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

KIT_ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("qrclima_release_builder", KIT_ROOT / "tools/build_package.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
spec = importlib.util.spec_from_file_location("qrclima_release_profile", KIT_ROOT / "public/scripts/profile_store.py")
store = importlib.util.module_from_spec(spec)
spec.loader.exec_module(store)
ROOT_FILES = {"README.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "ARCHITECTURE.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE", "acceptance.md", "verification.md", ".gitignore", ".gitattributes"}
SOURCE_TYPES = {"public": {".md", ".json", ".py"}, "starter": {".md", ".html"}, "tools": {".py"}, "tests": {".py"}, "docs": {".md"}}
PRIVATE_PARTS = {".qrclima", "profiles", "receipts", "context", "workspace", "dist", "output", "__pycache__", "profile.json", "journal.jsonl"}
TOKEN_PATTERN = re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}")
MACHINE_PATH = re.compile(r"\b[A-Za-z]:[\\/](?:Users|TESIVIL|Desarrollo)[\\/]", re.I)


class ReleaseError(ValueError):
    pass


def allowed_path(name):
    path = PurePosixPath(name)
    if path.is_absolute() or "\\" in name or ".." in path.parts or not path.parts:
        return False
    if any(part.casefold() in PRIVATE_PARTS or part.casefold().startswith(("private", ".env")) for part in path.parts):
        return False
    if name in ROOT_FILES or name in {"starter/.gitignore", ".github/workflows/check.yml"}:
        return True
    return len(path.parts) > 1 and path.parts[0] in SOURCE_TYPES and path.suffix in SOURCE_TYPES[path.parts[0]]


def check_entry(name, contents):
    if not allowed_path(name):
        raise ReleaseError("Un archivo queda fuera de las rutas publicas permitidas.")
    try:
        content = contents.decode("utf-8")
    except UnicodeError as exc:
        raise ReleaseError("Un archivo publico no es texto UTF-8.") from exc
    if store.SECRET_PATTERN.search(content) or TOKEN_PATTERN.search(content) or MACHINE_PATH.search(content):
        raise ReleaseError("Se detecto un formato de secreto o ruta privada del equipo.")
    if name.endswith(".json"):
        store.reject_secrets(json.loads(content))


def source_entries(root=KIT_ROOT):
    root = Path(root).resolve()
    names = [name for name in ROOT_FILES if (root / name).exists()]
    for directory in (*SOURCE_TYPES, ".github"):
        source = root / directory
        if not source.exists():
            continue
        if builder.is_link(source):
            raise ReleaseError("Una raiz publica es un enlace.")
        for path in sorted(source.rglob("*")):
            if "__pycache__" in path.relative_to(root).parts:
                continue
            if builder.is_link(path):
                raise ReleaseError("Hay un enlace dentro de las fuentes publicas.")
            if path.is_file():
                names.append(path.relative_to(root).as_posix())
    entries = {}
    for name in sorted(names):
        if builder.is_link(root / name):
            raise ReleaseError("Un archivo publico es un enlace.")
        contents = (root / name).read_bytes()
        check_entry(name, contents)
        entries[name] = contents
    return entries


def git(root, *args, allow_failure=False):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode and not allow_failure:
        raise ReleaseError("No se pudo comprobar Git; verifica repositorio, indice e historial disponibles.")
    return result


def check_index(root=KIT_ROOT):
    count = 0
    for item in git(root, "ls-files", "--stage", "-z").stdout.split(b"\0"):
        if not item:
            continue
        metadata, raw_name = item.split(b"\t", 1)
        mode, oid, stage = metadata.decode("ascii").split()
        if mode not in {"100644", "100755"} or stage != "0":
            raise ReleaseError("El indice contiene un enlace, submodulo o conflicto.")
        check_entry(raw_name.decode("utf-8"), git(root, "cat-file", "blob", oid).stdout)
        count += 1
    if not count:
        raise ReleaseError("El indice publico esta vacio.")
    return count


def check_history(root=KIT_ROOT):
    revisions = git(root, "rev-list", "--all", allow_failure=True)
    if revisions.returncode:
        raise ReleaseError("No se pudo inspeccionar el historial de Git.")
    seen = set()
    commits = revisions.stdout.decode("ascii").splitlines()
    for commit in commits:
        for item in git(root, "ls-tree", "-r", "-z", commit).stdout.split(b"\0"):
            if not item:
                continue
            metadata, raw_name = item.split(b"\t", 1)
            mode, kind, oid = metadata.decode("ascii").split()
            name = raw_name.decode("utf-8")
            if not allowed_path(name) or mode not in {"100644", "100755"} or kind != "blob":
                raise ReleaseError("El historial contiene archivos fuera del contrato publico.")
            if (name, oid) not in seen:
                check_entry(name, git(root, "cat-file", "blob", oid).stdout)
                seen.add((name, oid))
    return len(commits)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracked", action="store_true", help="Inspect the exact staged Git blobs")
    parser.add_argument("--history", action="store_true", help="Also inspect all locally reachable committed files")
    args = parser.parse_args()
    try:
        entries = source_entries()
        builder.validate_public()
        workspace = builder.workspace_entries()
        counts = {"public_source_files": len(entries), "workspace_files": len(workspace)}
        if args.tracked:
            counts["staged_files"] = check_index()
        if args.history:
            counts["commits_checked"] = check_history()
        print(json.dumps(counts, sort_keys=True))
        print("Control de publicacion correcto. Revisa tambien el contenido personal en lenguaje natural.")
    except (ValueError, OSError, UnicodeError) as exc:
        message = str(exc) if isinstance(exc, (ReleaseError, builder.PackageError, store.ProfileError)) else "Fallo de formato o archivos en las fuentes publicas."
        parser.exit(2, message + "\n")


if __name__ == "__main__":
    main()
