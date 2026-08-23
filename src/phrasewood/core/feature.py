"""Features — the typed variables that hold a world's state.

A :class:`Feature` is a *definition*: a name, a :class:`FeatureType`, and a
default. It is immutable and lives on the authored ``Tree``. The *current value*
of a feature lives in a ``World`` (see :mod:`phrasewood.state.world`).

The type is a small class hierarchy rather than a tagged field, so that each
type owns its own rules for validating, coercing, and clamping values — and so
that a new kind of feature is a new class, not another branch in a growing
``if`` ladder.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Final

from phrasewood.errors import FeatureValueError


class FeatureType(ABC):
    """The type of a feature: it knows how to validate, coerce, and clamp values.

    Subclasses implement :meth:`coerce` (accept a valid value or raise) and
    :meth:`natural_default` (the value used when a feature gives no default of
    its own). :meth:`clamp` is optional and defaults to a no-op.
    """

    @abstractmethod
    def coerce(self, value: Any) -> Any:
        """Return ``value`` normalized to this type, or raise ``FeatureValueError``."""

    @abstractmethod
    def natural_default(self) -> Any:
        """The value a feature of this type takes when it declares no default."""

    def clamp(self, value: Any) -> Any:
        """Constrain an already-coerced value to any bounds. No bounds by default."""
        return value


@dataclass(frozen=True)
class IntType(FeatureType):
    """A whole number, optionally bounded by ``min`` and/or ``max`` (inclusive)."""

    min: int | None = None
    max: int | None = None

    def __post_init__(self) -> None:
        if self.min is not None and self.max is not None and self.min > self.max:
            raise FeatureValueError(f"int min ({self.min}) is greater than max ({self.max})")

    def coerce(self, value: Any) -> int:
        # bool is a subclass of int in Python; reject it so True/False never
        # silently masquerade as 1/0 in a numeric feature.
        if isinstance(value, bool) or not isinstance(value, int):
            raise FeatureValueError(f"expected an integer, got {type(value).__name__}: {value!r}")
        return value

    def clamp(self, value: int) -> int:
        if self.min is not None and value < self.min:
            return self.min
        if self.max is not None and value > self.max:
            return self.max
        return value

    def natural_default(self) -> int:
        # 0 where possible; otherwise the nearest bound (e.g. min=3 -> 3).
        return self.clamp(0)


@dataclass(frozen=True)
class BoolType(FeatureType):
    """A true/false flag."""

    def coerce(self, value: Any) -> bool:
        if not isinstance(value, bool):
            raise FeatureValueError(f"expected a boolean, got {type(value).__name__}: {value!r}")
        return value

    def natural_default(self) -> bool:
        return False


@dataclass(frozen=True)
class TextType(FeatureType):
    """A short piece of text."""

    def coerce(self, value: Any) -> str:
        if not isinstance(value, str):
            raise FeatureValueError(f"expected text, got {type(value).__name__}: {value!r}")
        return value

    def natural_default(self) -> str:
        return ""


@dataclass(frozen=True)
class EnumType(FeatureType):
    """One of a fixed set of named values (e.g. ``"wary" | "warm" | "cold"``)."""

    values: tuple[str, ...]

    def __post_init__(self) -> None:
        # Accept any sequence of strings and freeze it to a tuple.
        normalized = tuple(self.values)
        if not normalized:
            raise FeatureValueError("an enum feature needs at least one value")
        for v in normalized:
            if not isinstance(v, str):
                raise FeatureValueError(f"enum values must be text, got {type(v).__name__}: {v!r}")
        if len(set(normalized)) != len(normalized):
            raise FeatureValueError(f"enum values must be unique: {normalized}")
        object.__setattr__(self, "values", normalized)

    def coerce(self, value: Any) -> str:
        if value not in self.values:
            raise FeatureValueError(f"{value!r} is not one of {list(self.values)}")
        return value

    def natural_default(self) -> str:
        return self.values[0]


class _Unset:
    """Sentinel distinguishing 'no default given' from a default of 0/False/''."""

    _instance: _Unset | None = None

    def __new__(cls) -> _Unset:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return "<unset>"


UNSET: Final = _Unset()


@dataclass(frozen=True)
class Feature:
    """A named, typed slot of world state — e.g. ``Feature("trust", IntType(0, 5))``.

    If ``default`` is omitted, the type's natural default is used. Any default
    given is validated up front, so an impossible default fails loudly at
    definition time rather than mysteriously at play time.
    """

    name: str
    type: FeatureType
    default: Any = UNSET
    help: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            raise FeatureValueError("a feature needs a non-empty name")
        if self.default is UNSET:
            object.__setattr__(self, "default", self.type.natural_default())
        else:
            object.__setattr__(self, "default", self.normalize(self.default))

    def normalize(self, value: Any) -> Any:
        """Coerce and clamp an arbitrary value into a valid value for this feature."""
        try:
            return self.type.clamp(self.type.coerce(value))
        except FeatureValueError as exc:
            raise FeatureValueError(f"feature {self.name!r}: {exc}") from exc


__all__ = [
    "FeatureType",
    "IntType",
    "BoolType",
    "TextType",
    "EnumType",
    "Feature",
    "UNSET",
]
