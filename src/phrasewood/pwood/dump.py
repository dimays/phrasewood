"""Writing a Tree back to `.pwood` files.

`save(tree, path)` renders a tree to the **canonical** layout — one entity per
file, one bud per file — and writes either a folder or a zipped `.pwood`. The
loader reads many shapes (a list in one file, inline in the manifest); the writer
picks one clean form. Only meaningful fields are written: defaults and empties are
left out, so the output stays terse and re-reads to the same tree.

The YAML is emitted with plain PyYAML — no comment preservation — because the
serializer exists to export machine-built trees and to prove round-trip data
fidelity, not to re-print hand-authored files.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

import yaml

from phrasewood.core import BoolType, EnumType, IntType, TextType
from phrasewood.core.bud import Action, Bud, Choice
from phrasewood.core.entity import Entity
from phrasewood.core.feature import Feature
from phrasewood.core.tree import Tree
from phrasewood.errors import PhrasewoodError

FORMAT_VERSION = "0.1"


def save(tree: Tree, path: str | Path) -> Path:
    """Write a tree to a folder, or (if `path` ends in `.pwood`) a zipped file."""
    files = _render(tree)
    target = Path(path)
    if target.suffix == ".pwood":
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
            for relpath, text in files.items():
                archive.writestr(relpath, text)
    else:
        for relpath, text in files.items():
            out = target / relpath
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
    return target


def _render(tree: Tree) -> dict[str, str]:
    files = {"pwood.yaml": _dump(_manifest_dict(tree))}
    if tree.features:
        files["features.yaml"] = _dump({f.name: _feature_dict(f) for f in tree.features})
    for entity in tree.entities:
        files[f"entities/{entity.id}.yaml"] = _dump(_entity_dict(entity))
    for bud in tree.buds:
        files[f"buds/{bud.id}.md"] = _bud_text(bud)
    return files


def _dump(data: dict[str, Any]) -> str:
    # sort_keys=False keeps our field order; wide width keeps expressions on one line.
    return yaml.safe_dump(
        data, sort_keys=False, allow_unicode=True, default_flow_style=False, width=4096
    )


def _manifest_dict(tree: Tree) -> dict[str, Any]:
    data: dict[str, Any] = {"format": FORMAT_VERSION, "id": tree.id}
    for key in ("title", "author", "version", "created", "blurb", "start"):
        value = getattr(tree, key)
        if value:
            data[key] = value
    return data


def _feature_dict(feature: Feature) -> dict[str, Any]:
    ftype = feature.type
    data: dict[str, Any] = {}
    if isinstance(ftype, IntType):
        data["type"] = "int"
        if ftype.min is not None:
            data["min"] = ftype.min
        if ftype.max is not None:
            data["max"] = ftype.max
    elif isinstance(ftype, BoolType):
        data["type"] = "bool"
    elif isinstance(ftype, TextType):
        data["type"] = "text"
    elif isinstance(ftype, EnumType):
        data["type"] = "enum"
        data["values"] = list(ftype.values)
    else:  # pragma: no cover - every built-in type is handled above
        raise PhrasewoodError(f"cannot serialize feature type {type(ftype).__name__}")
    if feature.default != ftype.natural_default():
        data["default"] = feature.default
    if feature.help:
        data["help"] = feature.help
    return data


def _entity_dict(entity: Entity) -> dict[str, Any]:
    data: dict[str, Any] = {"id": entity.id}
    if entity.kind != "thing":
        data["kind"] = entity.kind
    if entity.name != entity.id:
        data["name"] = entity.name
    if entity.aliases:
        data["aliases"] = list(entity.aliases)
    if entity.description:
        data["description"] = entity.description
    if entity.features:
        data["features"] = {f.name: _feature_dict(f) for f in entity.features}
    return data


def _bud_text(bud: Bud) -> str:
    front = _dump(_bud_front(bud)).rstrip("\n")
    return f"---\n{front}\n---\n{bud.content}\n"


def _bud_front(bud: Bud) -> dict[str, Any]:
    data: dict[str, Any] = {"id": bud.id}
    if bud.title:
        data["title"] = bud.title
    if bud.when is not None:
        data["when"] = bud.when
    if bud.once:
        data["once"] = True
    if bud.tags:
        data["tags"] = list(bud.tags)
    if bud.choices:
        data["choices"] = [_choice_dict(c) for c in bud.choices]
    if bud.actions:
        data["actions"] = [_action_dict(a) for a in bud.actions]
    return data


def _choice_dict(choice: Choice) -> dict[str, Any]:
    data: dict[str, Any] = {"label": choice.label}
    _add_option_fields(data, choice)
    return data


def _action_dict(action: Action) -> dict[str, Any]:
    data: dict[str, Any] = {"verb": action.verb}
    if action.aliases:
        data["aliases"] = list(action.aliases)
    _add_option_fields(data, action)
    return data


def _add_option_fields(data: dict[str, Any], option: Choice | Action) -> None:
    if option.when is not None:
        data["when"] = option.when
    if option.do is not None:
        data["do"] = option.do
    if option.goto is not None:
        data["goto"] = option.goto


__all__ = ["save"]
