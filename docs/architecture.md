# Architecture

How the engine is put together, and the few ideas that keep it small. For the
reasoning behind each choice, see [`../DECISIONS.md`](../DECISIONS.md).

## The one rule: definitions vs. state

Everything splits in two:

- **Definitions** — immutable, authored: `Feature`, `Entity`, `Bud`, and the whole
  `Tree`. This is what a `.pwood` file will load into.
- **State** — mutable, per-playthrough: the `World` (current feature values, entity
  state, bloom history).

One `Tree` spins up many independent `World`s; `World.for_tree(tree)` makes one.
This split is why the model is easy to test, and why the future browser runtime can
share the same definitions while holding its own state per player.

## The stack

Dependencies point one way only — `engine → state → core → expr → errors`:

| Package | Holds |
| --- | --- |
| `core/` | the authored definitions: `feature`, `entity`, `bud`, `tree` |
| `state/` | mutable state: `FeatureStore`, `World`, and the `WorldEnvironment` adapter |
| `expr/` | the `when` / `do` language: `tokens` → `parser` → `nodes` (AST) → `evaluator`, plus the `Environment` interface |
| `engine/` | the bloom loop: `Session`, the `Selector` policy, and the terminal `play` loop |
| `errors.py` | the `PhrasewoodError` family |

A `FeatureStore` is the shared "validated bag of features" that backs both the
world's own features and each entity's — so a value is coerced and clamped by its
feature the same way wherever it lives.

## Two pluggable seams

The engine depends on interfaces, not concretions:

- **`Environment`** (`expr/`) — how an expression resolves and assigns names. The
  evaluator never touches a `World`; it asks an `Environment`. `WorldEnvironment` is
  today's implementation; entity- and helper-aware ones plug in later.
- **`Selector`** (`engine/`) — which bud blooms when several are eligible.
  `PrioritySelector` and `MenuSelector` ship; more (and author-chosen policies) join
  without touching the loop.

Same pattern both times: a tiny interface, swappable implementations. It is what
holds the door open for the TypeScript runtime and for handing authors control over
sequencing.

## The bloom loop

`Session` is a small state machine over a `Tree` + `World`:

1. `view()` reports what to show — a bud (`content` + available options), a menu of
   eligible buds, or an ending (with its final passage).
2. `choose(index)` takes the player's pick: it runs the option's effect, then either
   follows a `goto` to a named bud or asks the `Selector` what blooms next.
3. A bud's `when` gates only *open selection*; a `goto` blooms directly. A menu of
   one auto-blooms; the just-left bud is held out of open selection to avoid trivial
   loops.

The terminal `play` loop is a thin wrapper over this surface, with input and output
injected so it is fully testable.

## Compile once

`when` / `do` strings are parsed to AST when a bud/choice/action is constructed, not
each time they run. Syntax errors surface at authoring time; play evaluates cached
trees.

## Why this shape

The whole design points at one future fact: a **second implementation** of this
engine will run in the browser, in TypeScript, playing the same `.pwood` games. So
the model is plain data, the language is strict and fully specified, and the moving
parts hide behind small interfaces. Nothing here assumes it is the only runtime.
