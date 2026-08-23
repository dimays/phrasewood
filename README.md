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
