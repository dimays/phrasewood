"""The World — the mutable state of a single playthrough.

Where the ``Tree`` is what the author wrote (immutable), the :class:`World` is
what is happening *right now*: the current value of every feature. One tree can
spawn many independent worlds, which is exactly how the platform will run many
players through the same story at once.

A world is backed by a :class:`~phrasewood.state.store.FeatureStore` for its
world-level features. Entity state and bloom history join it in later commits.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from typing import Any

from phrasewood.core.feature import Feature
from phrasewood.state.store import FeatureStore


class World:
    """Holds the current value of every world-level feature.

    Reads and writes delegate to a :class:`FeatureStore`, so values are validated
    and clamped by their feature definitions on every write.
    """

    def __init__(
        self,
        features: Iterable[Feature],
        values: Mapping[str, Any] | None = None,
    ) -> None:
        self._store = FeatureStore(features, values)

    # -- world features ----------------------------------------------------

    def get(self, name: str) -> Any:
        """Return the current value of a feature, or raise ``UnknownFeature``."""
        return self._store.get(name)

    def set(self, name: str, value: Any) -> Any:
        """Set a feature's value (validated and clamped). Returns the stored value."""
        return self._store.set(name, value)

    def has(self, name: str) -> bool:
        """Whether a feature by this name is defined in the world."""
        return self._store.has(name)

    def features(self) -> tuple[Feature, ...]:
        """The world-level feature definitions, in definition order."""
        return self._store.features()

    def snapshot(self) -> dict[str, Any]:
        """A plain-dict copy of the current world-feature values."""
        return self._store.snapshot()

    def reset(self, name: str | None = None) -> None:
        """Reset one feature to its default, or all features when ``name`` is None."""
        self._store.reset(name)

    # -- mapping-style sugar (over world features) -------------------------

    def __getitem__(self, name: str) -> Any:
        return self._store.get(name)

    def __setitem__(self, name: str, value: Any) -> None:
        self._store.set(name, value)

    def __contains__(self, name: object) -> bool:
        return name in self._store

    def __iter__(self) -> Iterator[str]:
        return iter(self._store)

    def __len__(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        inner = ", ".join(f"{name}={self._store.get(name)!r}" for name in self._store)
        return f"World({inner})"


__all__ = ["World"]
