"""Loading a `.pwood` project into a Tree.

`load(path)` reads either a project **folder** or a zipped **`.pwood`** file. It
reads the YAML, coerces every value through `schema`, and hands the pieces to the
model — so the model's own validation (compile-at-construction, duplicate ids,
dangling `goto`s) does the deep checking for free.

Buds load in **sorted filename order**; prefix filenames (`01-bridge.md`) to
control it — the bud's `id` lives in the frontmatter, independent of the filename.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any, Protocol

import yaml

from phrasewood.core import Tree
from phrasewood.errors import LoadError, PhrasewoodError
from phrasewood.pwood import schema
from phrasewood.pwood.frontmatter import split_frontmatter


def load(path: str | Path) -> Tree:
    """Load a `.pwood` project (a folder or a zipped file) into a Tree."""
    return _build_tree(_open(path))


class _Source(Protocol):
    label: str

    def read(self, relpath: str) -> str | None: ...
    def list(self, reldir: str) -> list[str]: ...


class _DirSource:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.label = str(root)

    def read(self, relpath: str) -> str | None:
        target = self.root / relpath
        return target.read_text(encoding="utf-8") if target.is_file() else None

    def list(self, reldir: str) -> list[str]:
        target = self.root / reldir
        if not target.is_dir():
            return []
        return sorted(child.name for child in target.iterdir() if child.is_file())


class _ZipSource:
    def __init__(self, path: Path) -> None:
        self.zip = zipfile.ZipFile(path)
        self.label = str(path)
        self.prefix = _zip_prefix(self.zip)

    def read(self, relpath: str) -> str | None:
        try:
            return self.zip.read(self.prefix + relpath).decode("utf-8")
        except KeyError:
            return None

    def list(self, reldir: str) -> list[str]:
        base = f"{self.prefix}{reldir.rstrip('/')}/"
        names = []
        for name in self.zip.namelist():
            if name.startswith(base) and not name.endswith("/"):
                tail = name[len(base) :]
                if "/" not in tail:
                    names.append(tail)
        return sorted(names)


def _open(path: str | Path) -> _Source:
    resolved = Path(path)
    if not resolved.exists():
        raise LoadError(f"no such path: {resolved}")
    if resolved.is_dir():
        return _DirSource(resolved)
    if zipfile.is_zipfile(resolved):
        return _ZipSource(resolved)
    raise LoadError(f"not a .pwood project (expected a folder or a zip file): {resolved}")


def _zip_prefix(zf: zipfile.ZipFile) -> str:
    names = zf.namelist()
    if "pwood.yaml" in names:
        return ""
    for name in names:
        if name.endswith("/pwood.yaml"):
            return name[: -len("pwood.yaml")]
    raise LoadError("this .pwood zip has no pwood.yaml")


def _yaml(text: str, where: str) -> Any:
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise LoadError(f"{where}: invalid YAML: {exc}") from exc


def _build_tree(source: _Source) -> Tree:
    manifest_text = source.read("pwood.yaml")
    if manifest_text is None:
        raise LoadError(f"{source.label}: missing pwood.yaml")
    manifest = schema.as_map(_yaml(manifest_text, "pwood.yaml") or {}, "pwood.yaml")
    if "id" not in manifest:
        raise LoadError("pwood.yaml: missing 'id'")

    features = _collect_features(source, manifest)
    entities = _collect_entities(source, manifest)

    buds = []
    for name in source.list("buds"):
        if not name.endswith((".md", ".markdown")):
            continue
        where = f"buds/{name}"
        front_text, body = split_frontmatter(source.read(where) or "", where)
        front = schema.as_map(_yaml(front_text, where) or {}, where)
        buds.append(schema.build_bud(front, body, where))

    try:
        return Tree(
            id=schema.as_str(manifest["id"], "pwood.yaml.id"),
            title=schema.opt_str(manifest, "title", "pwood.yaml.title", "") or "",
            author=schema.opt_str(manifest, "author", "pwood.yaml.author", "") or "",
            version=schema.opt_str(manifest, "version", "pwood.yaml.version", "") or "",
            created=schema.opt_str(manifest, "created", "pwood.yaml.created", "") or "",
            blurb=schema.opt_str(manifest, "blurb", "pwood.yaml.blurb", "") or "",
            features=features,
            entities=tuple(entities),
            buds=tuple(buds),
            start=schema.opt_str(manifest, "start", "pwood.yaml.start", "") or "",
        )
    except PhrasewoodError as exc:
        raise LoadError(f"{source.label}: {exc}") from exc


def _each(data: Any, where: str) -> list[Any]:
    """A definition source may be one mapping, or a list of them. Normalize to a list."""
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    raise LoadError(f"{where}: expected a mapping or a list")


def _collect_features(source: _Source, manifest: dict[str, Any]) -> tuple[Any, ...]:
    """Features from an inline manifest `features:` and/or a `features.yaml` file."""
    specs: list[tuple[str, Any, str]] = []
    if manifest.get("features"):
        inline = schema.as_map(manifest["features"], "pwood.yaml.features")
        specs += [(name, spec, "pwood.yaml.features") for name, spec in inline.items()]
    text = source.read("features.yaml")
    if text is not None:
        fmap = schema.as_map(_yaml(text, "features.yaml") or {}, "features.yaml")
        specs += [(name, spec, "features.yaml") for name, spec in fmap.items()]
    return tuple(schema.build_feature(name, spec, where) for name, spec, where in specs)


def _collect_entities(source: _Source, manifest: dict[str, Any]) -> list[Any]:
    """Entities from an inline manifest `entities:` and/or files under `entities/`.

    Each source may hold a single entity (a mapping) or several (a list).
    """
    entities = []
    if "entities" in manifest:
        inline = manifest["entities"]
        for i, data in enumerate(_each(inline, "pwood.yaml.entities")):
            where = (
                f"pwood.yaml.entities[{i}]" if isinstance(inline, list) else "pwood.yaml.entities"
            )
            entities.append(schema.build_entity(data, where))
    for name in source.list("entities"):
        if not name.endswith((".yaml", ".yml")):
            continue
        base = f"entities/{name}"
        parsed = _yaml(source.read(base) or "", base)
        for i, data in enumerate(_each(parsed, base)):
            where = f"{base}[{i}]" if isinstance(parsed, list) else base
            entities.append(schema.build_entity(data, where))
    return entities


__all__ = ["load"]
