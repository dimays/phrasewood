# The `.pwood` format — draft v0

> **Status: draft for Phase 2.** The engine model this describes is now implemented
> (Phase 1); this spec is how that model will be represented on disk, and the
> loader/serializer is Phase 2 work. The *shape* — a folder of text files, zipped to
> a single `.pwood` — is locked; the TOML field names below may still shift as we
> build the loader.

## What a project is

A Phrasewood game is a **tree**. On disk, a tree is a **folder of human-readable
text files** — so it diffs cleanly and lives happily in git. To share or upload
one, you zip that folder into a single **`.pwood`** file (a zip with a manifest
inside, the way `.docx`, `.epub`, and `.love` work). The engine can load either
form.

```
the-lamplighters-debt/
├── pwood.toml            # manifest: what this tree is, and where it starts
├── features.toml        # the world's state variables and their defaults
├── entities/             # things, people, places (one file each)
│   ├── ferryman.toml
│   └── lantern.toml
└── buds/                 # the story, one bud per file
    ├── the-broken-bridge.md
    └── ask-the-ferryman.md
```

A **sprig** (a tiny game) may collapse this to a single folder with just
`pwood.toml` and a `buds/` directory — everything else is optional.

## The model, in one paragraph

The world is a bag of **features** (typed state). **Buds** are units of story
that declare, via a `when` expression, the state under which they may **bloom**.
At any moment the engine knows which buds are eligible; the player advances by
taking a **choice** or typing a phrase that maps to an **action**, either of
which applies **effects** (state changes) and may hand control to another bud via
`goto`. **Entities** are named bundles of their own features that buds and
expressions can reach. That's the whole loop.

---

## `pwood.toml` — the manifest

```toml
[pwood]
format = "0.0"                 # the .pwood format version this project targets

[tree]
id = "the-lamplighters-debt"
title = "The Lamplighter's Debt"
author = "David Mays"
blurb = "The bridge is out, and the ferryman knows your name."
start = "the-broken-bridge"    # id of the bud that blooms first
```

## `features.toml` — the world's state

Each entry declares one feature. Supported `type`s (v0): `int`, `bool`, `text`,
`enum`.

```toml
[trust_in_ferryman]
type = "int"
default = 0
min = 0                        # optional clamp
max = 5
help = "How far the ferryman trusts you."

[has_lantern]
type = "bool"
default = true

[chapter]
type = "int"
default = 1
```

## `entities/*.toml` — things, people, places

```toml
[entity]
id = "ferryman"
kind = "character"             # character | place | thing | (author-defined)
name = "the ferryman"
aliases = ["ferryman", "boatman", "him"]   # nouns the phrase line will accept
description = "A hooded figure at the oars, patient as the tide."

[features]                    # entity-local state, same shapes as above
mood = { type = "enum", values = ["wary", "warm", "cold"], default = "wary" }
```

Reference an entity's feature in expressions as `ferryman.mood`.

## `buds/*.md` — the story

Each bud is a Markdown file: **TOML frontmatter** (delimited by `+++`) carries the
structured data; the **Markdown body** is the prose the player reads.

```markdown
+++
id = "ask-the-ferryman"
title = "Ask him how"          # a short label, shown when this bud is offered in a menu
when = "chapter == 1 and trust_in_ferryman < 3"
once = false                   # if true, this bud can bloom at most once
tags = ["conversation"]

[[choice]]
label = "Offer the lantern as payment"
when = "has_lantern"           # optional: hide this choice unless true
do = "has_lantern = false; trust_in_ferryman += 2; ferryman.mood = 'warm'"
goto = "the-crossing"

[[choice]]
label = "Ask what he knows of your father"
do = "trust_in_ferryman += 1"

[[action]]                     # phrase-line verbs → effects
verb = "pay"
aliases = ["give lantern", "offer the lantern", "hand over the lantern"]
when = "has_lantern"
do = "has_lantern = false; trust_in_ferryman += 2"
goto = "the-crossing"
+++

The ferryman does not look up. "The bridge?" he says. "The bridge has been out
since your father's time." Rain runs from the brim of his hood.
```

- **`choice`** — an explicit, tappable option. `label` shown to the player;
  optional `when` gates visibility; `do` applies effects; `goto` transitions.
- **`action`** — a phrase-line verb. `aliases` widen what typed input matches;
  otherwise identical to a choice. (Choices and actions unify at runtime.)
- **`goto`** blooms a bud directly, *bypassing its `when`*. A bud meant to be reached
  only by a link carries `when = "false"` to stay out of open selection.
- Prose body will support light templating and variation in a later draft
  (e.g. showing text conditionally, or picking one of several phrasings).

---

## The expression & effect layer

`when` and `do` are written in Phrasewood's small, safe expression language —
integer arithmetic, boolean logic, comparisons, and `feature` / `entity.feature`
references. It is specified in full (and identically for the browser runtime) in
[`expression-language.md`](expression-language.md).

```
when = "chapter == 1 and trust_in_ferryman < 3"
do   = "has_lantern = false; trust_in_ferryman += 2; ferryman.mood = 'warm'"
```

`goto` is not part of the language — it is a field on a choice/action that names the
next bud, applied after the effect runs.

---

## The runtime loop (informative)

This is the shape the loader feeds; the engine that runs it is described in
[`architecture.md`](architecture.md).

1. **Load** the project → a `Tree` (definitions) and a fresh `World` (state).
2. **Bloom** the `start` bud, marking it bloomed.
3. **Present** the current bud's prose plus its available choices/actions.
4. **Take** an option: apply its `do` effects, then follow its `goto` if present —
   otherwise ask the **selector** which eligible bud blooms next (or offer the player
   a menu of them).
5. **End** when no bud is eligible; a leaf bud with no successors ends on its prose.

## Open questions (for Phase 2)

- **Selection policy** — *resolved.* A pluggable `Selector` (player-menu default +
  priority) decides among eligible buds; more policies, and per-tree/per-pool choice,
  are the direction. See [`../DECISIONS.md`](../DECISIONS.md).
- **Text variation & conditional prose** syntax in the body.
- **Namespacing / includes** for large trees, and how a **grove** references its
  member trees.
- Whether `features.toml` and `entities/` should be inlinable into `pwood.toml`
  for the smallest sprigs.
