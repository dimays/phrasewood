"""FeatureStore — a validated bag of features and their current values.

This is the shared heart of mutable state. A :class:`~phrasewood.state.world.World`
is backed by one store for its world-level features, and (once entities exist)
each entity is backed by one for its own features — so validating and clamping a
value works identically wherever that value lives.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from typing import Any

from phrasewood.core.feature import Feature
from phrasewood.errors import DuplicateFeature, UnknownFeature


class FeatureStore:
    """Holds the current value of every feature it was built with, keyed by name.

    Values are validated and clamped through their feature definitions on every
    write, so a store can never hold a value its features would reject.
    """

    def __init__(
        self,
        features: Iterable[Feature],
        values: Mapping[str, Any] | None = None,
    ) -> None:
        self._features: dict[str, Feature] = {}
        for feature in features:
            if feature.name in self._features:
                raise DuplicateFeature(f"duplicate feature name {feature.name!r}")
            self._features[feature.name] = feature

        # Start every feature at its default, then apply any opening overrides.
        self._values: dict[str, Any] = {
            name: feature.default for name, feature in self._features.items()
        }
        if values:
            for name, value in values.items():
                self.set(name, value)

    # -- reads -------------------------------------------------------------

    def get(self, name: str) -> Any:
        """Return the current value of a feature, or raise ``UnknownFeature``."""
        try:
            return self._values[name]
        except KeyError:
            raise UnknownFeature(f"no feature named {name!r}") from None

    def has(self, name: str) -> bool:
        """Whether a feature by this name is in the store."""
        return name in self._features

    def features(self) -> tuple[Feature, ...]:
        """The feature definitions, in definition order."""
        return tuple(self._features.values())

    def snapshot(self) -> dict[str, Any]:
        """A plain-dict copy of the current values (safe to read or store)."""
        return dict(self._values)

    # -- writes ------------------------------------------------------------

    def set(self, name: str, value: Any) -> Any:
        """Set a feature's value (validated and clamped). Returns the stored value."""
        feature = self._definition(name)
        stored = feature.normalize(value)
        self._values[name] = stored
        return stored

    def reset(self, name: str | None = None) -> None:
        """Reset one feature to its default, or all features when ``name`` is None."""
        if name is None:
            for key, feature in self._features.items():
                self._values[key] = feature.default
            return
        self._values[name] = self._definition(name).default

    # -- mapping-style sugar ----------------------------------------------

    def __getitem__(self, name: str) -> Any:
        return self.get(name)

    def __setitem__(self, name: str, value: Any) -> None:
        self.set(name, value)

    def __contains__(self, name: object) -> bool:
        return name in self._features

    def __iter__(self) -> Iterator[str]:
        return iter(self._features)

    def __len__(self) -> int:
        return len(self._features)

    def __repr__(self) -> str:
        inner = ", ".join(f"{name}={value!r}" for name, value in self._values.items())
        return f"FeatureStore({inner})"

    # -- internals ---------------------------------------------------------

    def _definition(self, name: str) -> Feature:
        try:
            return self._features[name]
        except KeyError:
            raise UnknownFeature(f"no feature named {name!r}") from None


__all__ = ["FeatureStore"]
