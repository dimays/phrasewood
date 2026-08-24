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

from phrasewood.core.entity import Entity
from phrasewood.core.feature import Feature
from phrasewood.errors import DuplicateEntity, UnknownEntity, UnknownFeature
from phrasewood.state.store import FeatureStore


class World:
    """Holds the current value of every world-level and entity-level feature.

    Reads and writes delegate to a :class:`FeatureStore` — one for world-level
    features, and one per entity — so values are validated and clamped by their
    feature definitions on every write, wherever they live.
    """

    def __init__(
        self,
        features: Iterable[Feature],
        entities: Iterable[Entity] = (),
        values: Mapping[str, Any] | None = None,
    ) -> None:
        self._store = FeatureStore(features, values)
        self._entities: dict[str, Entity] = {}
        self._entity_stores: dict[str, FeatureStore] = {}
        for entity in entities:
            if entity.id in self._entities:
                raise DuplicateEntity(f"duplicate entity id {entity.id!r}")
            self._entities[entity.id] = entity
            self._entity_stores[entity.id] = FeatureStore(entity.features)

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

    # -- entities ----------------------------------------------------------

    def has_entity(self, entity_id: str) -> bool:
        """Whether an entity by this id is defined in the world."""
        return entity_id in self._entities

    def entities(self) -> tuple[Entity, ...]:
        """The entity definitions, in definition order."""
        return tuple(self._entities.values())

    def entity(self, entity_id: str) -> Entity:
        """Return an entity definition, or raise ``UnknownEntity``."""
        try:
            return self._entities[entity_id]
        except KeyError:
            raise UnknownEntity(f"no entity named {entity_id!r}") from None

    def get_entity_feature(self, entity_id: str, feature_name: str) -> Any:
        """Return the current value of one of an entity's features."""
        store = self._entity_store(entity_id)
        if not store.has(feature_name):
            raise UnknownFeature(f"entity {entity_id!r} has no feature named {feature_name!r}")
        return store.get(feature_name)

    def set_entity_feature(self, entity_id: str, feature_name: str, value: Any) -> Any:
        """Set one of an entity's features (validated and clamped)."""
        store = self._entity_store(entity_id)
        if not store.has(feature_name):
            raise UnknownFeature(f"entity {entity_id!r} has no feature named {feature_name!r}")
        return store.set(feature_name, value)

    def entity_snapshot(self, entity_id: str) -> dict[str, Any]:
        """A plain-dict copy of one entity's current feature values."""
        return self._entity_store(entity_id).snapshot()

    def _entity_store(self, entity_id: str) -> FeatureStore:
        try:
            return self._entity_stores[entity_id]
        except KeyError:
            raise UnknownEntity(f"no entity named {entity_id!r}") from None

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
