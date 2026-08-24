"""The Tree — a whole authored story, immutable.

A :class:`Tree` gathers the metadata (who wrote it, when, which version), the
feature and entity definitions, the buds, and which bud blooms first. It is what
a ``.pwood`` file loads into, and what a ``World`` is spun up from.

Construction validates the story's integrity: no duplicate ids, and every
``start`` / ``goto`` points at a bud that actually exists — so a broken link is
caught when the tree is built, not when a player walks into it.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from phrasewood.core.bud import Bud
from phrasewood.core.entity import Entity
from phrasewood.core.feature import Feature
from phrasewood.errors import (
    DuplicateBud,
    DuplicateEntity,
    DuplicateFeature,
    PhrasewoodError,
    UnknownBud,
)


def _reject_duplicates(ids: Iterable[str], error: type[PhrasewoodError], label: str) -> None:
    seen: set[str] = set()
    for value in ids:
        if value in seen:
            raise error(f"duplicate {label} {value!r}")
        seen.add(value)


@dataclass(frozen=True)
class Tree:
    """A single authored story."""

    id: str
    title: str = ""
    author: str = ""
    version: str = ""
    created: str = ""  # ISO-8601 date string, kept as text for clean serialization
    blurb: str = ""
    features: tuple[Feature, ...] = ()
    entities: tuple[Entity, ...] = ()
    buds: tuple[Bud, ...] = ()
    start: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            raise PhrasewoodError("a tree needs a non-empty id")

        object.__setattr__(self, "features", tuple(self.features))
        object.__setattr__(self, "entities", tuple(self.entities))
        object.__setattr__(self, "buds", tuple(self.buds))

        _reject_duplicates((f.name for f in self.features), DuplicateFeature, "feature")
        _reject_duplicates((e.id for e in self.entities), DuplicateEntity, "entity")
        _reject_duplicates((b.id for b in self.buds), DuplicateBud, "bud")

        bud_ids = {b.id for b in self.buds}
        if self.start and self.start not in bud_ids:
            raise UnknownBud(f"start bud {self.start!r} is not defined")
        for bud in self.buds:
            for target in bud.gotos():
                if target not in bud_ids:
                    raise UnknownBud(f"bud {bud.id!r} points to unknown bud {target!r}")

    def has_bud(self, bud_id: str) -> bool:
        """Whether a bud by this id exists in the tree."""
        return any(bud.id == bud_id for bud in self.buds)

    def bud(self, bud_id: str) -> Bud:
        """Return a bud by id, or raise ``UnknownBud``."""
        for bud in self.buds:
            if bud.id == bud_id:
                return bud
        raise UnknownBud(f"no bud named {bud_id!r}")


__all__ = ["Tree"]
