# Decisions

A living record of the choices that shape Phrasewood, with the reasoning behind
each so future-us (and contributors) don't relitigate settled ground. Newest
sections may still move; anything marked **Locked** should not change without a
deliberate reversal noted here.

---

## Vocabulary — **Locked**

One small, consistent lexicon, drawn from the "wood of phrases" the name hints at.

| Term         | Meaning |
| ------------ | ------- |
| **feature**  | a typed variable holding world state (inventory, skills, relationships, progress) |
| **bud**      | the atomic unit of story; *blooms* when the current state satisfies its requirements |
| **entity**   | a thing, person, or place that carries its own features |
| **tree**     | a single story / game |
| **grove**    | a collection of stories |
| **sprig**    | a tiny, constrained game — a cutting bearing just a few buds |
| **the phrase line** | the always-present input where a player can *type* a phrase, not only tap a choice |
| **the Coauthor** | the single (opt-in, paid) AI collaborator — a chat build door *and* in-studio help; never the author |
| **Phrasewood+** | the paid platform tier |

Notes on why:

- **bud** replaces the borrowed term "storylet." "leaf" was the first pick but its
  irregular plural (`leaves`) is a papercut in code; `buds` is clean, and "a bud
  blooms" is the exact verb we want for "becomes available."
- **feature** replaces "quality" — the term of art in QBN. Same concept, but a
  less ambiguous word with a cleaner regular plural (`features`, not `qualities`).
- The primitives are deliberately few. Depth comes from *composition*, not from a
  large surface area.

## The systemic model, not branching — **Locked**

The engine is built on **buds + features** (a quality-based / storylet model),
not hand-wired branches. Branching is the trivial case of it.

*Why:* branch-wiring is what makes large stories collapse into spaghetti (the
classic Twine wall). If availability is *computed* from declared requirements,
authors add moments without managing a combinatorial web of links, and the story
scales.

*Prior art (we didn't invent this):* quality-based narrative / storylets, from
Failbetter Games (*Fallen London*, StoryNexus), analyzed by Emily Short, and
formalized by Kreminski & Wardrip-Fruin, *"Sketching a Map of the Storylets
Design Space"* (2018). See the README for links. "Bud" is our name for a
storylet.

## What removes the ceiling — **Locked**

The pressure valve for "I need to do something the primitives don't cover" is the
**systemic model plus a small, safe expression layer** for requirements and
effects — *not* arbitrary embedded code in published games. Authors who want to
go further can build on this open-source engine directly on their own machine.

*Why:* it keeps the platform's runtime safe and portable (see Runtime) while
still avoiding a hard creative ceiling.

## The package is the engine, not a build mode — **Locked**

This package (`pip install phrasewood`) is the open-source core the platform runs
on, and the canonical definition of what a Phrasewood game *is*. It exists for
local/terminal play, developer experimentation, and open contribution. You *can*
hand-author a game against it, but the platform's supported build doors are the
visual studio and the Coauthor — not writing Python.

## Runtime & safety — **Locked (revised 2026-08-24)**

The platform plays games **server-side with this Python engine** — one codebase.
A playthrough's state is just the choices made so far (plus a random seed; see
below), carried in a token in the page, so the server is **stateless**: it replays
the choices each turn to render the current view. This reuses the engine directly
and scales cheaply for read-paced text play.

*Safety holds trivially.* Published games are pure **data** (`.pwood`), never
author code, so our own trusted engine reads trusted data — there is no untrusted
code to sandbox, on server or client. (The earlier worry was untrusted *Python* in
a browser — Pyodide/WASM escapes, DEF CON 34, CVE-2026-5752 — which simply doesn't
exist once games are data. That's also why the server-sandbox tier was dropped.)

*Superseded.* We previously planned a TypeScript **data runtime** to play games
client-side. That is now **deferred future work**, to be built only if offline /
static / embeddable / zero-latency play becomes a real need — at which point a
Python-generated **conformance suite** keeps it in lockstep with this engine. The
client-side motivation was never safety (games are data); it was those
nice-to-haves, not anything 1.0 requires.

## Randomness must be seeded — **Locked**

All engine randomness — a random selector, a dice function in a `do`, a
probabilistic challenge — must flow through a **single seeded, specified PRNG**
whose seed is part of the play state, never an ambient `random()`. One rule, three
payoffs: **replay determinism** (stateless server-side play reproduces the same
random outcomes), **cross-runtime parity** (a future TS runtime draws identically
from the same seed), and **stable display** (re-rendering a turn doesn't reshuffle).
The engine has no randomness yet; this rule governs the first feature that adds it,
and the PRNG algorithm must be specified (not language-default) so both runtimes
match.

## The phrase line & its cost model — **Locked**

Player input is a **hybrid**: tappable choices by default, with a phrase line
always available to type into. Typed input resolves through a cascade, cheapest
first:

0. exact / alias / fuzzy string matching against the current bud's actions
1. semantic match via a tiny embedding model, with per-action embeddings
   precomputed at publish time
2. a real model — **only** on the rare residual — behind a
   `(game, bud-state, phrase)` cache
3. graceful fallback to tappable choices if nothing resolves (or a budget is spent)

Tiers 0–1 run in the player's own browser, so the common path costs the platform
nothing and scales for free. AI here only ever *maps a typed phrase to an action
the author already wrote* — it never generates story text.

*Why:* it makes typed play (which the name invites) a first-class joy without
reviving "guess the verb," and without letting AI cost grow with the user base.

## AI stance — **Locked**

AI is a **muse and a bounded mechanic, never the author.** Build-time help
(rehearsal, a continuity conscience, idea seeds) and the runtime phrase-line
mapping are the sanctioned uses. No one-click game generation.

## Definitions vs. state — **Locked**

Everything the author writes is an immutable **definition** (`Feature`, `Entity`,
`Bud`, and the whole `Tree`); everything that changes during play lives in a
mutable **`World`**. One tree spins up many independent worlds (`World.for_tree`).

*Why:* it keeps "what was written" cleanly apart from "what's happening," makes the
model trivially testable, and maps exactly onto the browser data runtime — the same
definitions, with a separate world per player.

## Compile once, at construction — **Locked**

A bud, choice, or action parses its `when` / `do` strings into cached AST the moment
it is built. Syntax errors surface at authoring time, not mid-play, and the engine
evaluates the compiled form. The source strings are kept, so a tree round-trips back
to `.pwood` unchanged. (Convention: `when` / `do` are the source; `condition` /
`effect` are their compiled forms.)

## Explicit transitions vs. open selection — **Locked**

A `goto` blooms a named bud **directly, bypassing its `when`** — it is an authored
"go here now." A bud's `when` governs only its eligibility in *open selection* (when
no `goto` applies and the engine must choose among eligible buds). A bud meant to be
reached only by a link therefore carries `when = "false"` to stay out of open
selection while remaining goto-able.

## Selection is a pluggable policy — **Locked (interface); growing (policies)**

When several buds are eligible and no `goto` decides, a **`Selector`** chooses what
blooms — or defers to the player. Two ship today: **player-menu** (the default;
offer the eligible buds) and **priority** (first in tree order; deterministic).
Weighted-random, salience, and deck-based policies are designed-for but deferred —
they need a seeded, specified PRNG for cross-runtime parity.

*Direction:* the intent is to **hand authors the keys** — pick a policy per tree,
and eventually per pool of buds (a main thread on priority, an ambient pool on
random, a hub on menu). The `Selector` interface is the seam that keeps that
additive. See Kreminski & Wardrip-Fruin for the map of this space.

## Strict, specified expression semantics — **Locked**

The `when` / `do` language is deliberately strict so the Python engine and the future
TypeScript runtime agree exactly: integer-only arithmetic with floor division,
integer-only ordered comparisons, equality that keeps a bool distinct from an int
(`true == 1` is `false`), and short-circuiting boolean logic. It is safe by
construction — only the constructs we implement exist, so there is no arbitrary code
to sandbox. Full reference: [`docs/expression-language.md`](docs/expression-language.md).

## Two pluggable seams — **Locked**

The engine reaches state and sequencing only through small interfaces —
**`Environment`** (how expressions read and write state) and **`Selector`** (which
bud blooms). Concrete state, entities, and policies plug in without changing the
evaluator or the loop. This is the pattern that lets the browser runtime and
author-chosen policies drop in cleanly later. See
[`docs/architecture.md`](docs/architecture.md).

## Format — **Locked (shape); draft (details)**

Our own format, extension **`.pwood`**. A project is a folder of human-readable
text files while you author (git-friendly, diffable), zipped into a single
`.pwood` file to distribute (as `.docx` / `.epub` / `.love` do). The engine model is
now implemented (Phase 1); the on-disk schema is drafted in
[`docs/pwood-format.md`](docs/pwood-format.md) and its loader/serializer arrives in
Phase 2.

The files are **YAML** (manifest, features, entities), with **buds as Markdown +
YAML frontmatter** — chosen for comfortable hand-editing, comments, natural
multi-line prose, and parseability in both runtimes. This ends the zero-dependency
run (YAML is stdlib in neither Python nor JS); `PyYAML` is the one runtime dep, and
we stay on Python 3.10.

*The one sharp edge, and the rule that dulls it:* YAML *infers* scalar types, and
parsers disagree at the edges (the "Norway problem" — `no`/`on`/`yes` may become
booleans; PyYAML follows YAML 1.1, js-yaml 1.2). So the loader **`safe_load`s and
then coerces every value to its schema type**, never trusting YAML's inference.
That keeps the Python and browser runtimes identical *and* is the safety rule for
loading untrusted games (`safe_load` only — never `yaml.load`).

---

## Roadmap

Each phase is many small, gated commits, and each ends on something playable.

0. **Foundations** ✓ — repo, scaffold, this doc, the first-draft format spec.
1. **Engine core** ✓ — features, buds, entities, the expression language, the bloom
   loop (`Session` + pluggable `Selector`), and a terminal player. `pip install
   phrasewood`, playable end to end, fully tested.
2. **The `.pwood` format** — *(next)* serialize/deserialize the model to the folder
   form and back; author a reference game as files and load it.
3. **Play in the browser** — *(next)* server-side Django play (the Python engine, stateless replay), no login; a new platform repo. (The client-side TS runtime is deferred — see Runtime & safety.)
4. **The Make studio** — the bud-centric visual builder, the computed map, a live playtest, and the first sprigs.
5. **The commons** — accounts, publishing, discovery, follow, "surprise me," and Trust & Safety (see below).
6. **The Coauthor & the phrase line** — the opt-in, paid AI layer and forgiving typed input. Ships *with* 1.0.

## Platform context (out of scope for this repo, tracked for coherence)

- **Monetization:** the creative act is free (play, visual studio, publish, local
  play); Phrasewood+ charges for the Coauthor and scale. Aligns the paywall with
  real compute cost and keeps AI optional.
- **Trust & Safety (formalize at Phase 5, needs a lawyer's pass):** play needs no
  login; publishing is gated behind a verified one. Reactive reporting + light
  automated screening on publish + a discovery gate for unvetted work + maturity
  labels + written ToS/Content/Privacy. Hard legal floor: CSAM reporting, a
  registered DMCA agent, 13+ terms.
