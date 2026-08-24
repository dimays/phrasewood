# The expression & effect language

The tiny language behind a bud's `when` (a requirement) and `do` (its effects). It
is intentionally minimal, **safe** (no arbitrary code — only the constructs below
exist), and **fully specified**, because a second implementation will run in the
browser and must behave identically.

This is a reference. For how it fits the engine, see [`architecture.md`](architecture.md).

## Grammar

```
expr       := or
or         := and ("or" and)*
and        := not ("and" not)*
not        := "not" not | comparison
comparison := sum (("=="|"!="|"<"|"<="|">"|">=") sum)?
sum        := term (("+"|"-") term)*
term       := factor (("*"|"/") factor)*
factor     := INT | STRING | "true" | "false" | NAME | NAME "." NAME | "(" expr ")"

effect     := stmt (";" stmt)*
stmt       := ref ("=" | "+=" | "-=") expr
ref        := NAME | NAME "." NAME
```

**Notation:** `:=` is "is defined as"; `"x"` is a literal; `UPPERCASE` is a token
(`INT` like `3`, `STRING` like `'warm'`, `NAME` like `trust`); `|` is alternatives;
`( )` groups; `*` is zero-or-more; `?` is optional. The rules are layered
loosest-first (`or` at the top, `factor` at the bottom), which is what encodes
operator precedence — so `a or b and c` means `a or (b and c)`, and `2 + 3 * 4`
means `2 + (3 * 4)`.

## Values

Three value types: **int**, **bool**, and **text**. An enum feature's value is text.

## Expression semantics

Strict, for cross-runtime parity:

- **Arithmetic** `+ - * /` — integers only. `/` is **floor division**; divide-by-zero
  is an error.
- **Ordered comparison** `< <= > >=` — integers only.
- **Equality** `== !=` — any values, but a bool is distinct from an int, so
  `true == 1` is `false` and `true == true` is `true`.
- **Boolean** `and or not` — operands must be booleans; `and` / `or` short-circuit
  (the right side isn't evaluated once the result is decided).
- **Comparison does not chain** — `1 < x < 5` is a syntax error; write
  `1 < x and x < 5`.
- **References** — `name` reads a world feature; `entity.name` reads an entity's
  feature.

Errors are raised, never guessed: an unknown name, a type mismatch, or bad syntax
each stops with a clear message rather than a silent wrong answer.

## Effects

A `do` string is one or more `;`-separated statements:

- `ref = expr` — set a value.
- `ref += expr` / `ref -= expr` — adjust an integer (both sides must be integers).

`ref` is `name` (a world feature) or `entity.name` (an entity's feature). Writes go
through the feature's own validation, so a value is coerced and clamped just like any
other write — `trust += 100` lands at the feature's max.

`goto` is **not** part of this language. It is a field on a choice or action that
names the next bud, applied *after* the effect runs.

## Examples

```
when:  trust >= 3 and has_lantern
when:  ferryman.mood == 'warm'
do:    trust += 2; ferryman.mood = 'warm'
do:    gold = gold - price
```

## Known gaps and candidates

- **No unary minus yet** — write `0 - 1`, not `-1`.
- **Bloom-history helpers** are candidates, not yet wired: `bloomed('bud-id')`,
  `visits('bud-id')`. The data already exists (`World` tracks bloom counts); only the
  syntax is missing.
