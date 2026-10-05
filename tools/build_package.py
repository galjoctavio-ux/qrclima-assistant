"""Build a local, public-only QRclima plugin archive. Never publishes or installs."""
import argparse
import importlib.util
import json
import posixpath
import re
import stat
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

KIT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = KIT_ROOT / "public"
STARTER_ROOT = KIT_ROOT / "starter"
ALLOWED_SUFFIXES = {".md", ".json", ".py"}
PRIVATE_NAMES = {"profile.json", "journal.jsonl", "profiles", "receipts", ".env"}


class PackageError(ValueError):
    pass


def is_link(path):
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def public_files(public_root=PUBLIC_ROOT):
    public_root = Path(public_root)
    if is_link(public_root):
        raise PackageError("La raiz publica no puede ser un enlace o punto de reanalisis.")
    public_root = public_root.resolve()
    files = []
    for path in sorted(public_root.rglob("*")):
        relative = path.relative_to(public_root)
        if "__pycache__" in relative.parts:
            continue
        if is_link(path):
            raise PackageError("El paquete contiene un enlace; se cancelo la construccion.")
        if any(part in PRIVATE_NAMES or part.lower().startswith("private") or part.startswith(".env") for part in relative.parts):
            raise PackageError("Hay archivos privados dentro de la raiz publica.")
        if path.is_dir():
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            raise PackageError("El paquete contiene un tipo de archivo no permitido.")
        files.append(path)
    if not files:
        raise PackageError("El paquete esta vacio.")
    return files


def validate_links(path, content, public_root):
    for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", content):
        target = target.strip().strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme in {"https", "http", "mailto"} or target.startswith("#"):
            continue
        if parsed.scheme or not parsed.path:
            raise PackageError("El paquete contiene un enlace de archivo no portable.")
        resolved = (path.parent / unquote(parsed.path)).resolve()
        if not resolved.is_relative_to(public_root) or not resolved.exists():
            raise PackageError(f"Referencia interna no resuelta en {path.relative_to(public_root)}.")


def validate_public(public_root=PUBLIC_ROOT):
    files = public_files(public_root)
    public_root = Path(public_root).resolve()
    spec = importlib.util.spec_from_file_location("qrclima_profile_store", PUBLIC_ROOT / "scripts/profile_store.py")
    store = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(store)
    for path in files:
        content = path.read_text(encoding="utf-8")
        if store.SECRET_PATTERN.search(content):
            raise PackageError("Se detecto un formato de secreto en el paquete.")
        if path.suffix.lower() == ".json":
            data = json.loads(content)
            store.reject_secrets(data)
        elif path.suffix.lower() == ".md":
            validate_links(path, content, public_root)
    manifest = json.loads((public_root / "plugin.json").read_text(encoding="utf-8"))
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", manifest.get("name", "")):
        raise PackageError("Nombre de plugin invalido.")
    if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")) or not manifest.get("description"):
        raise PackageError("El manifiesto necesita version y descripcion.")
    skills = list((public_root / "skills").glob("*/SKILL.md"))
    if not skills:
        raise PackageError("No hay skills para empaquetar.")
    return files


def build_package(output, public_root=PUBLIC_ROOT):
    files = validate_public(public_root)
    public_root = Path(public_root).resolve()
    output = Path(output).resolve()
    if output.is_relative_to(public_root):
        raise PackageError("El ZIP debe guardarse fuera de la raiz publica.")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation: rebuilding cannot silently replace a reviewed archive.
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(public_root).as_posix())
        if is_link(KIT_ROOT / "LICENSE"):
            raise PackageError("La licencia no puede ser un enlace.")
        archive.write(KIT_ROOT / "LICENSE", "LICENSE")
    return len(files) + 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--format", choices=("workspace", "plugin"), default="workspace")
    parser.add_argument("--workspace-dir", help="Create a fresh project folder as well as the workspace ZIP")
    args = parser.parse_args()
    try:
        if args.format == "workspace":
            entries = workspace_entries()
            if Path(args.output).exists():
                raise PackageError("El ZIP ya existe; usa una ruta nueva para esta revision.")
            if args.workspace_dir:
                write_workspace(args.workspace_dir, entries)
            count = build_workspace_archive(args.output, entries)
        else:
            if args.workspace_dir:
                raise PackageError("workspace-dir solo corresponde al formato workspace.")
            count = build_package(args.output)
        print(f"ZIP local creado: {Path(args.output).resolve()} ({count} archivos publicos).")
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        message = str(exc) if isinstance(exc, PackageError) else "No se construyo el ZIP; revisa formato, ruta y que no exista ya."
        parser.exit(2, message + "\n")


def workspace_entries():
    files = validate_public()
    entries = {".agents/" + path.relative_to(PUBLIC_ROOT).as_posix(): path.read_bytes() for path in files if path.name != "plugin.json" and path != PUBLIC_ROOT / "AGENTS.md"}
    for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", "COMPATIBILIDAD.md", "README.md", "EMPIEZA-AQUI.html", ".gitignore"):
        source = STARTER_ROOT / name
        if is_link(source):
            raise PackageError("La plantilla de inicio contiene un enlace.")
        entries[name] = source.read_bytes()
    manifest = json.loads((PUBLIC_ROOT / "plugin.json").read_text(encoding="utf-8"))
    entries["VERSION.json"] = (json.dumps({"name": manifest["name"], "version": manifest["version"], "format": "portable-agent-project", "private_data_included": False}, indent=2) + "\n").encode("utf-8")
    if is_link(KIT_ROOT / "LICENSE"):
        raise PackageError("La licencia no puede ser un enlace.")
    entries["LICENSE"] = (KIT_ROOT / "LICENSE").read_bytes()
    # Claude entry points refer to the canonical procedure; never fork its logic.
    for skill in sorted((PUBLIC_ROOT / "skills").glob("*/SKILL.md")):
        frontmatter = skill.read_text(encoding="utf-8").split("---", 2)[1]
        entries[f".claude/skills/{skill.parent.name}/SKILL.md"] = ("---" + frontmatter + "---\n\nLee el [procedimiento compartido](../../../.agents/skills/" + skill.parent.name + "/SKILL.md) y aplícalo. Resuelve sus referencias desde ese archivo original. Esta entrada no cambia permisos ni instala herramientas.\n").encode("utf-8")
    spec = importlib.util.spec_from_file_location("qrclima_workspace_store", PUBLIC_ROOT / "scripts/profile_store.py")
    store = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(store)
    for name, contents in entries.items():
        content = contents.decode("utf-8")
        if store.SECRET_PATTERN.search(content):
            raise PackageError("Se detecto un formato de secreto en la plantilla.")
        if name.endswith(".json"):
            store.reject_secrets(json.loads(content))
        targets = re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", content) if name.endswith(".md") else re.findall(r'href="([^"\n]+)"', content) if name.endswith(".html") else []
        for target in targets:
            parsed = urlsplit(target.strip().strip("<>"))
            if parsed.scheme in {"http", "https", "mailto"} or target.startswith("#"):
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path)))
            if parsed.scheme or resolved.startswith("../") or resolved not in entries and not any(key.startswith(resolved + "/") for key in entries):
                raise PackageError(f"Referencia interna no portable en {name}.")
    return entries


def write_workspace(directory, entries=None):
    directory = Path(directory).resolve()
    if directory.is_relative_to(PUBLIC_ROOT.resolve()) or directory.is_relative_to(STARTER_ROOT.resolve()):
        raise PackageError("La carpeta generada debe estar fuera de las fuentes publicas.")
    entries = workspace_entries() if entries is None else entries
    directory.mkdir(parents=True, exist_ok=False)
    for name, contents in entries.items():
        target = (directory / name).resolve()
        if not target.is_relative_to(directory):
            raise PackageError("Un archivo sale de la carpeta de destino.")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(contents)
    return len(entries)


def build_workspace_archive(output, entries=None):
    entries = workspace_entries() if entries is None else entries
    output = Path(output).resolve()
    if output.is_relative_to(PUBLIC_ROOT.resolve()) or output.is_relative_to(STARTER_ROOT.resolve()):
        raise PackageError("El ZIP debe guardarse fuera de las fuentes publicas.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, contents in sorted(entries.items()):
            archive.writestr("Mi-asistente-QRclima/" + name, contents)
    return len(entries)


if __name__ == "__main__":
    main()
