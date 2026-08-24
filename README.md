# Phrasewood

**An engine for text games grown from buds and features.**

Phrasewood is the open-source core beneath [phrasewood.com](https://phrasewood.com) —
a platform and toolset for creating, sharing, and playing text-based games. This
package is the engine those games run on: a small, composable vocabulary for
building interactive stories you can play in a terminal, embed in your own tools,
or hack on directly.

> **Status: pre-alpha, and playable.** The engine works end to end — you can author
> a story in Python and play it at a prompt today. The on-disk `.pwood` format and
> the platform are still ahead, and the public API will change until 1.0.

## The idea

Most text-game tools force a trade-off: an easy on-ramp with a low ceiling, or a
high ceiling behind a cliff. Phrasewood's bet is a single systemic model that
scales from a five-minute toy to a simulated world without the author ever
hand-wiring a maze of branches.

The whole model is a handful of primitives:

| Term        | What it is                                                              |
| ----------- | ---------------------------------------------------------------------- |
| **feature** | a typed variable that holds part of the world's state (inventory, skills, mood, progress) |
| **bud**     | a unit of story that *blooms* when the current state meets its requirements |
| **entity**  | a thing, person, or place that carries its own features                |
| **tree**    | a single story                                                          |
| **grove**   | a collection of stories                                                 |
| **sprig**   | a tiny, constrained game — a cutting with just a few buds               |

Instead of drawing arrows between passages, you write buds and declare *when*
each can bloom. The reachable map emerges from those rules — so it scales.

## Why buds, not branches

Phrasewood did not invent this model. "Buds" is our name for **storylets**, part
of a design tradition usually called **quality-based narrative (QBN)**. Credit
belongs to the people who pioneered and mapped it:

- **[Failbetter Games](https://www.failbetter.com/)**, who built QBN into
  *[Fallen London](https://www.fallenlondon.com/)* (2009) and opened it to
  authors through their **StoryNexus** tool — the practical origin of storylets
  as most people know them.
- **[Emily Short](https://emshort.blog/)**, whose writing on quality-based,
  salience-based, and waypoint narrative structures is the clearest analysis of
  how and why these systems work.
- **Max Kreminski & Noah Wardrip-Fruin**, whose paper *"Sketching a Map of the
  Storylets Design Space"* (2018) gave the idea a shared vocabulary.

**Why we build on it instead of simple branching (the Twine model):** a branching
tree grows combinatorially — every meaningful choice multiplies the paths an
author must hand-wire and keep straight, and state management becomes unwieldy
as a story grows (the wall most Twine authors eventually hit). Storylets invert
the relationship: content is *decoupled* from a fixed graph. Each bud carries its
own conditions, so what's available is **computed from the world's state** rather
than wired by hand. Authors add moments locally without touching a web of global
links; stories stay maintainable at scale and can become systemic, emergent, and
deeply reactive. That scalability is the whole reason the model is worth adopting
— and worth giving good, joyful tooling.

## Try it

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/dimays/phrasewood.git
cd phrasewood
uv run phrasewood        # play the bundled game, "The Lamplighter's Debt"
```

Type a number to choose, or `q` to quit. The game is small on purpose — its ending
is *chosen by the world* rather than hard-wired, which is the whole model in
miniature.

## Author a game

A story is a `Tree` of buds. Requirements (`when`) and effects (`do`) are written
in a tiny, safe expression language — see
[`docs/expression-language.md`](docs/expression-language.md).

```python
from phrasewood import Tree, Bud, Choice, Feature, IntType, play

tree = Tree(
    id="small-wood",
    title="A Small Wood",
    features=(Feature("nerve", IntType(0, 3), default=0),),
    buds=(
        Bud(
            "start",
            once=True,
            content="A dark path splits the wood.",
            choices=(
                Choice("Steady your nerve", do="nerve += 2", goto="fork"),
                Choice("Hurry onward", goto="fork"),
            ),
        ),
        Bud(
            "fork",
            once=True,
            content="A narrow way drops into the dark.",
            choices=(
                Choice("Take the narrow way", when="nerve >= 2", goto="end"),
                Choice("Keep to the safe path", goto="end"),
            ),
        ),
        Bud("end", once=True, content="You reach the far side, changed by the wood."),
    ),
    start="start",
)

play(tree)  # play it in the terminal
```

Steady your nerve first and the narrow way opens; hurry, and it stays hidden. That
conditional choice is computed from state, not authored twice.

## Develop

This project uses [uv](https://docs.astral.sh/uv/).

```bash
uv run pytest        # run the tests
uv run ruff check    # lint
uv run ruff format   # format
```

## Where things are

- [`DECISIONS.md`](DECISIONS.md) — the choices that shape Phrasewood, and why.
- [`docs/architecture.md`](docs/architecture.md) — how the engine is put together.
- [`docs/expression-language.md`](docs/expression-language.md) — the `when` / `do` language reference.
- [`docs/pwood-format.md`](docs/pwood-format.md) — the draft `.pwood` on-disk format (arrives in Phase 2).
- [`src/phrasewood/examples/`](src/phrasewood/examples/) — bundled games, authored in Python.

## License

[MIT](LICENSE) © 2026 David Mays
