# Phrasewood

**An engine for text games grown from buds and qualities.**

Phrasewood is the open-source core beneath [phrasewood.com](https://phrasewood.com) —
a platform and toolset for creating, sharing, and playing text-based games. This
package is the engine those games run on: a small, composable vocabulary for
building interactive stories that you can play in a terminal, embed in your own
tools, or hack on directly.

> **Status: pre-alpha.** The design is settled and the engine is being built in
> the open, phase by phase. The public API will change until 1.0.

## The idea

Most text-game tools force a trade-off: an easy on-ramp with a low ceiling, or a
high ceiling behind a cliff. Phrasewood's bet is a single systemic model that
scales from a five-minute toy to a simulated world without the author ever
hand-wiring a maze of branches.

The whole model is a handful of primitives:

| Term        | What it is                                                              |
| ----------- | ---------------------------------------------------------------------- |
| **quality** | a typed variable that holds the world's state (inventory, skills, mood, progress) |
| **bud**     | a unit of story that *blooms* when the current state meets its requirements |
| **entity**  | a thing, person, or place that carries its own qualities               |
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

## Install

Requires Python 3.10+. While it's pre-release, install from source:

```bash
git clone https://github.com/dimays/phrasewood.git
cd phrasewood
uv sync
```

## Develop

This project uses [uv](https://docs.astral.sh/uv/).

```bash
uv run pytest        # run the tests
uv run ruff check    # lint
uv run ruff format   # format
```

## Where things are

- [`DECISIONS.md`](DECISIONS.md) — the locked design vocabulary and architecture, with the reasoning behind each call.
- [`docs/pwood-format.md`](docs/pwood-format.md) — a first draft of the `.pwood` on-disk project format.

## License

[MIT](LICENSE) © 2026 David Mays
