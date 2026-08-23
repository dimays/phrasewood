# The `.pwood` format — draft v0

> **Status: draft, provisional.** This sketches the on-disk shape of a Phrasewood
> project and the model behind it. It exists to give Phase 1 (the engine) a
> target to build toward; expect the details to shift as the engine model gets
> real. The *shape* (a folder of text files, zipped to a `.pwood` file) is
> locked; the field names and expression syntax below are not.

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
- Prose body will support light templating and variation in a later draft
  (e.g. showing text conditionally, or picking one of several phrasings).

---

## The expression & effect layer

Deliberately small and **safe** — no arbitrary code, so the same content runs in
the browser data runtime and the Python engine identically. This is the
"ceiling-remover" referenced in [`../DECISIONS.md`](../DECISIONS.md).

**Expressions** (`when`) evaluate to a boolean:

- references: `feature_name`, `entity.feature`
- comparisons: `== != < <= > >=`
- logic: `and`, `or`, `not`
- arithmetic: `+ - * /`
- literals: integers, `true` / `false`, `'single-quoted strings'`
- helpers (candidate): `bloomed('bud-id')`, `visits('bud-id')`

**Effects** (`do`) are a `;`-separated (or newline-separated) sequence of
mutations:

- `feature = <expr>`
- `feature += <n>` / `feature -= <n>`
- `entity.feature = <expr>`

`goto` is a field, not an effect — it names the transition after effects apply.

---

## The runtime loop (informative)

1. **Load** the project → a `World`: features at their defaults, entities built,
   buds indexed.
2. **Bloom** the `start` bud (or, in open/systemic play, compute the set of
   eligible buds whose `when` holds and `once` allows).
3. **Present** the current bud's prose plus its visible choices; accept a tapped
   choice or a typed phrase mapped to an action.
4. **Apply** the selected `do` effects, then follow `goto` if present, else
   recompute eligible buds.
5. **Repeat** until no bud is eligible or an explicit ending is reached.

## Open questions (for Phase 1 to answer)

- **Selection policy when several buds are eligible.** Directed flow (`goto`)
  covers authored sequences; open play needs a rule — priority, weighting,
  player-chosen menu (Fallen London style), or salience. Likely support several.
- **Endings.** An explicit `[[ending]]` construct, or simply "no eligible buds"?
- **Text variation & conditional prose** syntax in the body.
- **Namespacing / includes** for large trees, and how a **grove** references its
  member trees.
- Whether `features.toml` and `entities/` should be inlinable into `pwood.toml`
  for the smallest sprigs.
