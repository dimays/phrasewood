"""The Lamplighter's Debt — a small bundled game.

A three-minute piece that leans on the systemic model: one choice is gated by how
the ferryman regards you, and the ending is not reached by a ``goto`` but *chosen
by the world* — two ending buds sit behind mutually-exclusive requirements, so the
one that fits your ``trust`` blooms on its own. No conditional-prose feature
needed; the sequencing does it.
"""

from __future__ import annotations

from phrasewood.core import Bud, Choice, Entity, EnumType, Feature, IntType, Tree


def tree() -> Tree:
    """Build a fresh copy of the game."""
    return Tree(
        id="the-lamplighters-debt",
        title="The Lamplighter's Debt",
        author="David Mays",
        version="0.1.0",
        created="2026-08-24",
        blurb="The bridge is out, the rain is cold, and the ferryman knows your name.",
        features=(Feature("trust", IntType(0, 10), default=0),),
        entities=(
            Entity(
                "ferryman",
                kind="character",
                name="the ferryman",
                features=(Feature("mood", EnumType(("wary", "warm")), default="wary"),),
            ),
        ),
        buds=(
            Bud(
                "bridge",
                once=True,
                content=(
                    "The bridge is out. Rain needles the lantern glass, and the river "
                    "runs black and fast. At the dock a ferryman waits beneath a hood — "
                    "and when he looks up, he says your name."
                ),
                choices=(
                    Choice(
                        "Offer your lantern as payment",
                        do="trust += 3; ferryman.mood = 'warm'",
                        goto="ferry",
                    ),
                    Choice(
                        "Ask how he knows your name",
                        do="trust += 1",
                        goto="ferry",
                    ),
                ),
            ),
            Bud(
                "ferry",
                once=True,
                content=(
                    "You step aboard. He takes up the oars, and the far shore pulls "
                    "closer through the dark. For a while there is only the water."
                ),
                choices=(
                    Choice(
                        "Ask about the debt he mentioned",
                        when="trust >= 2",
                        goto="debt",
                    ),
                    Choice("Ride the rest of the way in silence"),
                ),
            ),
            Bud(
                "debt",
                once=True,
                # Reached only by the choice above. `when="false"` keeps it out of
                # open selection, while a goto still blooms it directly.
                when="false",
                content=(
                    '"Your father," he says, not turning, "lit the lamps on this '
                    "river for forty years, and never once asked to be paid. The debt "
                    "isn't yours to settle. But it's good you came to carry the light.\""
                ),
                choices=(Choice("Step ashore"),),
            ),
            Bud(
                "shore-warm",
                once=True,
                when="trust >= 3",
                content=(
                    "The far shore. The ferryman presses the lantern back into your "
                    "hands, its flame somehow unquenched by all that rain. In a window "
                    "up the hill, a lamp still burns, and someone is waiting up for you."
                ),
            ),
            Bud(
                "shore-cold",
                once=True,
                when="trust <= 2",
                content=(
                    "The far shore. The ferryman is already pushing off before your "
                    "second foot finds the stones. By the time you turn to thank him, "
                    "the dark has taken him, and the rain comes down as if it never knew "
                    "your name at all."
                ),
            ),
        ),
        start="bridge",
    )


__all__ = ["tree"]
