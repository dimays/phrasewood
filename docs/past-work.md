# Past work

Completed work, most recent first, stamped with a completion date. Items land here
from [`future-work.md`](future-work.md) as they ship.

## 2026-08-24 — Phase 2, the `.pwood` loader (PR #2)

`phrasewood.load(path)` reads a project folder or a zipped `.pwood` into a `Tree`.
The format pivoted from TOML to **YAML** (buds as Markdown + YAML frontmatter), with
the coerce-don't-infer discipline for cross-runtime parity. The CLI plays a path;
The Lamplighter's Debt was re-authored as real `.pwood` files.

## 2026-08-24 — Documentation refresh (PR #1)

Brought the docs in line with the completed engine: a playable README, engine-era
decisions recorded in `DECISIONS.md`, and two new docs — `architecture.md` and the
`expression-language.md` reference.

## 2026-08-24 — Phase 1, the engine core

Built the whole engine over a run of gated commits: the `Feature` model and `World`,
the safe `when`/`do` expression language, `FeatureStore` and entities, buds and the
`Tree`, the bloom loop (`Session` + pluggable `Selector`), and the terminal player
with a bundled game. `pip install phrasewood`, playable end to end, fully tested.

## 2026-08-23 — Phase 0, foundations

Created the public MIT-licensed repo (uv, `src/` layout) with the README,
`DECISIONS.md`, and the first-draft `.pwood` format spec.
