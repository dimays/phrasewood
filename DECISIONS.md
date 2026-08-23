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

## Runtime & safety — **Locked**

Two runtimes, one format:

- A **data runtime** interprets the `.pwood` format and is the one the platform
  ships to browsers (planned in TypeScript). It runs no untrusted code.
- This **Python engine** runs games on a developer's own machine.

*Why:* running untrusted Python in a visitor's browser is not safe today
(Pyodide/WASM sandbox escapes — DEF CON 34, CVE-2026-5752). Because custom code
is not a build mode, published games are pure data played by the safe runtime,
and Python only ever runs on its author's own hardware. This also removes any
need for server-side sandboxing at 1.0.

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

## Format — **Locked (shape); draft (details)**

Our own format, extension **`.pwood`**. A project is a folder of human-readable
text files while you author (git-friendly, diffable), zipped into a single
`.pwood` file to distribute (as `.docx` / `.epub` / `.love` do). The concrete
schema is drafted in [`docs/pwood-format.md`](docs/pwood-format.md) and will be
firmed up alongside the engine model (Phase 1) and its serializer (Phase 2).

---

## Roadmap

Each phase is many small, gated commits, and each ends on something playable.

0. **Foundations** — repo, scaffold, this doc, a first-draft format spec. *(this phase)*
1. **Engine core** — features, buds, entities, an expression layer, and a terminal player. `pip install phrasewood`, fully tested.
2. **The `.pwood` format** — serialize/deserialize the model to the folder form and back; author a reference game by hand.
3. **Play in the browser** — the TypeScript data runtime + a no-login web player; platform skeleton. *(separate repo)*
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
