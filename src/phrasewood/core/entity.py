"""Entities — the things, people, and places a story's state hangs on.

An :class:`Entity` is a *definition*, immutable and part of the authored ``Tree``:
its id, kind, display name, aliases (the nouns the phrase line will accept), and
its own features. The entity's *current* feature values live in a ``World``, just
like world-level features do — an entity is simply another bag of features.
"""

from __future__ import annotations

from dataclasses import dataclass

from phrasewood.core.feature import Feature
from phrasewood.errors import DuplicateFeature, PhrasewoodError


@dataclass(frozen=True)
class Entity:
    """A named thing that carries its own features — ``ferryman``, ``the-bridge``."""

    id: str
    kind: str = "thing"
    name: str = ""
    features: tuple[Feature, ...] = ()
    aliases: tuple[str, ...] = ()
    description: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            raise PhrasewoodError("an entity needs a non-empty id")

        # Accept any iterables on the way in; freeze them to tuples.
        object.__setattr__(self, "features", tuple(self.features))
        object.__setattr__(self, "aliases", tuple(self.aliases))

        # A missing display name falls back to the id.
        if not self.name:
            object.__setattr__(self, "name", self.id)

        seen: set[str] = set()
        for feature in self.features:
            if feature.name in seen:
                raise DuplicateFeature(
                    f"entity {self.id!r} has a duplicate feature {feature.name!r}"
                )
            seen.add(feature.name)

    def feature_names(self) -> tuple[str, ...]:
        """The names of this entity's own features, in definition order."""
        return tuple(feature.name for feature in self.features)


__all__ = ["Entity"]
