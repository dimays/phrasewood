# The `.pwood` format — draft v0.1

> **Status: draft, being implemented in Phase 2.** The engine model this describes
> is implemented (Phase 1); the loader that reads this format is in progress. The
> *shape* — a folder of text files, zipped to a single `.pwood` — is locked. Field
> names may still shift as the loader is built.

## What a project is

A Phrasewood game is a **tree**. On disk, a tree is a **folder of text files** —
so it diffs cleanly and lives happily in git. To share or upload one, you zip that
folder into a single **`.pwood`** file (a zip, the way `.docx`, `.epub`, and
`.love` work). The engine can load either form.

The files are **YAML**, chosen because it is comfortable to hand-edit, keeps
comments, handles multi-line prose well, and parses in both of Phrasewood's
runtimes (Python and, later, the browser).

```
the-lamplighters-debt/
├── pwood.yaml            # manifest: what this tree is, and where it starts
├── features.yaml         # the world's state variables and their defaults
├── entities/             # things, people, places (one file each)
│   └── ferryman.yaml
└── buds/                 # the story, one bud per file
    ├── bridge.md
    └── ask-the-ferryman.md
```

A **sprig** (a tiny game) may collapse this to a single folder with just
`pwood.yaml` and a `buds/` directory — everything else is optional.

## The model, in one paragraph

The world is a bag of **features** (typed state). **Buds** are units of story that
declare, via a `when` expression, the state under which they may **bloom**. The
player advances by taking a **choice** or typing a phrase that maps to an
**action**, either of which applies **effects** (state changes) and may hand
control to another bud via `goto`. **Entities** are named bundles of their own
features that buds and expressions can reach. That's the whole loop.

---

## `pwood.yaml` — the manifest

```yaml
format: "0.1"                  # the .pwood format version this project targets
id: the-lamplighters-debt
title: The Lamplighter's Debt
author: David Mays
version: "0.1.0"               # quote versions, or YAML reads 0.1.0-like values oddly
created: "2026-08-24"
blurb: The bridge is out, and the ferryman knows your name.
start: bridge                  # id of the bud that blooms first
```

## `features.yaml` — the world's state

A map of feature name → definition. Supported `type`s: `int`, `bool`, `text`,
`enum`.

```yaml
trust:
  type: int
  default: 0
  min: 0                       # optional clamp
  max: 10
  help: How far the ferryman trusts you.
chapter:
  type: int
  default: 1
```

## `entities/*.yaml` — things, people, places

```yaml
id: ferryman
kind: character                # character | place | thing | (author-defined)
name: the ferryman
aliases: [boatman, him]        # nouns the phrase line will accept
description: A hooded figure at the oars, patient as the tide.
features:                      # entity-local state, same shapes as above
  mood:
    type: enum
    values: [wary, warm, cold]
    default: wary
```

Reference an entity's feature in expressions as `ferryman.mood`.

## `buds/*.md` — the story

Each bud is a Markdown file: **YAML frontmatter** between `---` fences carries the
structured data; the **Markdown body** below is the prose the player reads. (This
is the familiar Jekyll/Hugo shape — metadata on top, a real prose document beneath.)

```markdown
---
id: ask-the-ferryman
title: Ask him how
when: chapter == 1 and trust < 3
once: false                    # if true, this bud can bloom at most once
tags: [conversation]
choices:
  - label: Offer the lantern as payment
    when: has_lantern          # optional: hide this choice unless true
    do: has_lantern = false; trust += 2; ferryman.mood = 'warm'
    goto: the-crossing
  - label: Ask what he knows of your father
    do: trust += 1
actions:                       # phrase-line verbs → effects
  - verb: pay
    aliases: [give lantern, offer the lantern]
    when: has_lantern
    do: has_lantern = false; trust += 2
    goto: the-crossing
---
The ferryman does not look up. "The bridge?" he says. "The bridge has been out
since your father's time." Rain runs from the brim of his hood.
```

- **`choice`** — a tappable option. `label` shown to the player; optional `when`
  gates visibility; `do` applies effects; `goto` transitions.
- **`action`** — a phrase-line verb. `aliases` widen what typed input matches;
  otherwise identical to a choice. (Choices and actions unify at runtime.)
- **`goto`** blooms a bud directly, *bypassing its `when`*. A bud meant to be reached
  only by a link carries `when: "false"` to stay out of open selection.
- Prose body will support light templating and variation in a later draft.

## A note on YAML typing

YAML *guesses* the type of unquoted scalars, and the guessing differs between
parsers (Python's PyYAML vs. the browser's js-yaml — the "Norway problem," where
`no`/`on`/`off`/`yes` may become booleans). To keep both runtimes identical, the
loader **parses safely and then coerces every value to its schema type** rather
than trusting YAML's inference. Two rules of thumb for authors:

- **Quote things that look like numbers or bools but aren't** — versions
  (`"0.1.0"`), and any enum value or id like `on`, `no`, `yes`.
- **Expressions are plain strings** — `when: trust >= 3` is fine unquoted; quote a
  `do`/`when` only if it contains a `:` followed by a space, or starts with a YAML
  indicator character.

---

## The expression & effect layer

`when` and `do` are written in Phrasewood's small, safe expression language,
specified in full in [`expression-language.md`](expression-language.md).

`goto` is not part of the language — it is a field on a choice/action that names
the next bud, applied after the effect runs.

---

## The runtime loop (informative)

The engine that runs a loaded tree is described in
[`architecture.md`](architecture.md).

1. **Load** the project → a `Tree` (definitions) and a fresh `World` (state).
2. **Bloom** the `start` bud, marking it bloomed.
3. **Present** the current bud's prose plus its available choices/actions.
4. **Take** an option: apply its `do` effects, then follow its `goto` if present —
   otherwise ask the **selector** which eligible bud blooms next (or offer the player
   a menu of them).
5. **End** when no bud is eligible; a leaf bud with no successors ends on its prose.

## Open questions (for Phase 2 and beyond)

- **Text variation & conditional prose** syntax in the body.
- **Namespacing / includes** for large trees, and how a **grove** references its
  member trees.
- Whether `features.yaml` and `entities/` should be inlinable into `pwood.yaml`
  for the smallest sprigs.
