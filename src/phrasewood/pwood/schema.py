"""Turning parsed YAML into model objects — safely.

Every value from YAML passes through a coercer here before it reaches the model.
We never trust YAML's implicit typing (which differs between parsers — the "Norway
problem"): each field is coerced to the type its schema expects, or a clear
``LoadError`` is raised. That is what keeps the Python and browser runtimes reading
the same file the same way.
"""

from __future__ import annotations

from typing import Any

from phrasewood.core import (
    Action,
    BoolType,
    Bud,
    Choice,
    Entity,
    EnumType,
    Feature,
    FeatureType,
    IntType,
    TextType,
)
from phrasewood.errors import LoadError, PhrasewoodError

# -- coercers --------------------------------------------------------------


def as_str(value: Any, field: str) -> str:
    """Coerce a scalar to text. A YAML bool becomes lowercase `true`/`false` so an
    unquoted `when: false` reads as the expression string, not Python's `False`."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return str(value)
    raise LoadError(f"{field}: expected text, got {type(value).__name__}")


def opt_str(data: dict[str, Any], key: str, field: str, default: str | None = None) -> str | None:
    if key in data and data[key] is not None:
        return as_str(data[key], field)
    return default


def as_bool(value: Any, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in ("true", "false"):
        return value.lower() == "true"
    raise LoadError(f"{field}: expected true or false, got {value!r}")


def as_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise LoadError(f"{field}: expected an integer, got {value!r}")
    return value


def as_str_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise LoadError(f"{field}: expected a list")
    return tuple(as_str(item, f"{field}[]") for item in value)


def as_map(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LoadError(f"{field}: expected a mapping")
    return value


def _as_list(value: Any, field: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise LoadError(f"{field}: expected a list")
    return value


def _opt_int(data: dict[str, Any], key: str, field: str) -> int | None:
    if key in data and data[key] is not None:
        return as_int(data[key], field)
    return None


# -- builders --------------------------------------------------------------


def build_feature(name: str, spec: Any, where: str) -> Feature:
    spec = as_map(spec, f"{where}.{name}")
    if "type" not in spec:
        raise LoadError(f"{where}: feature {name!r} is missing 'type'")
    ftype = _build_type(as_str(spec["type"], f"{where}.{name}.type"), spec, f"{where}.{name}")
    kwargs: dict[str, Any] = {}
    if "default" in spec and spec["default"] is not None:
        kwargs["default"] = spec["default"]  # raw; Feature coerces and clamps it
    help_text = opt_str(spec, "help", f"{where}.{name}.help", "")
    try:
        return Feature(name, ftype, help=help_text or "", **kwargs)
    except PhrasewoodError as exc:
        raise LoadError(f"{where}: feature {name!r}: {exc}") from exc


def _build_type(type_name: str, spec: dict[str, Any], where: str) -> FeatureType:
    if type_name == "int":
        return IntType(
            min=_opt_int(spec, "min", f"{where}.min"), max=_opt_int(spec, "max", f"{where}.max")
        )
    if type_name == "bool":
        return BoolType()
    if type_name == "text":
        return TextType()
    if type_name == "enum":
        if "values" not in spec:
            raise LoadError(f"{where}: an enum feature needs 'values'")
        return EnumType(as_str_list(spec["values"], f"{where}.values"))
    raise LoadError(f"{where}: unknown feature type {type_name!r}")


def build_entity(data: Any, where: str) -> Entity:
    data = as_map(data, where)
    if "id" not in data:
        raise LoadError(f"{where}: entity is missing 'id'")
    features: tuple[Feature, ...] = ()
    if data.get("features"):
        fmap = as_map(data["features"], f"{where}.features")
        features = tuple(build_feature(n, s, f"{where}.features") for n, s in fmap.items())
    try:
        return Entity(
            as_str(data["id"], f"{where}.id"),
            kind=opt_str(data, "kind", f"{where}.kind", "thing") or "thing",
            name=opt_str(data, "name", f"{where}.name", "") or "",
            features=features,
            aliases=as_str_list(data["aliases"], f"{where}.aliases") if data.get("aliases") else (),
            description=opt_str(data, "description", f"{where}.description", "") or "",
        )
    except PhrasewoodError as exc:
        raise LoadError(f"{where}: {exc}") from exc


def build_bud(front: Any, body: str, where: str) -> Bud:
    front = as_map(front, where)
    if "id" not in front:
        raise LoadError(f"{where}: bud is missing 'id'")
    choices = tuple(
        build_choice(c, f"{where}.choices[{i}]")
        for i, c in enumerate(_as_list(front.get("choices"), f"{where}.choices"))
    )
    actions = tuple(
        build_action(a, f"{where}.actions[{i}]")
        for i, a in enumerate(_as_list(front.get("actions"), f"{where}.actions"))
    )
    try:
        return Bud(
            as_str(front["id"], f"{where}.id"),
            content=body.strip(),
            title=opt_str(front, "title", f"{where}.title", "") or "",
            when=opt_str(front, "when", f"{where}.when"),
            once=as_bool(front["once"], f"{where}.once") if "once" in front else False,
            tags=as_str_list(front["tags"], f"{where}.tags") if front.get("tags") else (),
            choices=choices,
            actions=actions,
        )
    except PhrasewoodError as exc:
        raise LoadError(f"{where}: {exc}") from exc


def build_choice(data: Any, where: str) -> Choice:
    data = as_map(data, where)
    if "label" not in data:
        raise LoadError(f"{where}: choice is missing 'label'")
    try:
        return Choice(
            as_str(data["label"], f"{where}.label"),
            when=opt_str(data, "when", f"{where}.when"),
            do=opt_str(data, "do", f"{where}.do"),
            goto=opt_str(data, "goto", f"{where}.goto"),
        )
    except PhrasewoodError as exc:
        raise LoadError(f"{where}: {exc}") from exc


def build_action(data: Any, where: str) -> Action:
    data = as_map(data, where)
    if "verb" not in data:
        raise LoadError(f"{where}: action is missing 'verb'")
    try:
        return Action(
            as_str(data["verb"], f"{where}.verb"),
            aliases=as_str_list(data["aliases"], f"{where}.aliases") if data.get("aliases") else (),
            when=opt_str(data, "when", f"{where}.when"),
            do=opt_str(data, "do", f"{where}.do"),
            goto=opt_str(data, "goto", f"{where}.goto"),
        )
    except PhrasewoodError as exc:
        raise LoadError(f"{where}: {exc}") from exc
