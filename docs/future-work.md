# Future work

Planned and proposed work, grouped by area. This is a living backlog, not a
commitment — items move here when we decide to defer them, and move to
[`past-work.md`](past-work.md) (stamped with a completion date) when they ship.

## Phase 2 — the `.pwood` format

- [ ] **The serializer** — write a `Tree` back to `.pwood` files, with a full
  `Tree → files → Tree` round-trip. (Needs a YAML writer; decide PyYAML `dump`
  vs. `ruamel` if preserving author comments matters.)
- [ ] **Cross-file feature-definition library** — a named, reusable feature
  definition referenceable from any entity or file (define `mood` once, use it
  anywhere, with overrides). In-file reuse already works via YAML anchors; this is
  the across-file version, deferred until a real multi-file world needs it.
- [ ] **Ship a file-based example in the wheel** — so `.pwood` games can be played
  without a repo checkout (`importlib.resources`).

## The expression language

- [ ] **Unary minus** — write `-1`, not `0 - 1`.
- [ ] **Bloom-history helpers** — `bloomed('bud-id')`, `visits('bud-id')`. The data
  exists (`World` tracks bloom counts); only the syntax is unwired.

## The engine & sequencing

- [ ] **More selectors** — weighted-random (needs a seeded, specified PRNG for
  cross-runtime parity), salience, and StoryNexus-style deck/pinned.
- [ ] **Author-chosen policy** — pick a `Selector` per tree, and per *pool* of buds
  (a main thread on priority, an ambient pool on random, a hub on menu).
- [ ] **Explicit `priority` / `weight` bud fields** — when those selectors land.
- [ ] **Challenges** — probabilistic stat-checks (a StoryNexus idea worth borrowing).
- [ ] **Locations / settings** — an availability axis beyond feature conditions.

## Story authoring

- [ ] **Text variation & conditional prose** in a bud's body.
- [ ] **Namespacing / includes** for large trees; how a **grove** references its
  member trees.

## Platform (later phases)

- [ ] **Phase 3** — the TypeScript data runtime + a no-login web player (separate repo).
- [ ] **Phase 4** — the Make studio (bud-centric visual builder, computed map, live playtest).
- [ ] **Phase 5** — the commons (accounts, publishing, discovery) + Trust & Safety.
- [ ] **Phase 6** — the Coauthor & the forgiving phrase line (opt-in, paid).
- [ ] **Export / preservation** as a first-class feature — nothing ever trapped
  (the lesson from StoryNexus's shutdown).
