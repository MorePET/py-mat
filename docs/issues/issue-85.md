---
type: issue
state: closed
created: 2026-04-19T11:26:33Z
updated: 2026-04-19T11:31:50Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/85
comments: 0
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-20T04:51:02.328Z
---

# [Issue 85]: [pymat.search(query) — fuzzy search over the domain library (incl. grades)](https://github.com/MorePET/mat/issues/85)

## Summary

`pymat.search(query: str, *, limit: int = 10) -> list[Material]` as a top-level fuzzy-find over the loaded library. Complements `pymat.vis.search(...)` (visual catalog) with a symmetric domain-side verb.

## Design

Tokenized + weighted-target matching over a **flat** registry — grades, variants, vendors are already first-class:

- registry key: weight 10
- `Material.name` / `grade`: weight 5
- hierarchy parent names: weight 3

All tokens must match somewhere (conjunctive). Ties broken by shorter key.

Triggers `load_all()` so results are exhaustive. Case-insensitive.

## Examples

```python
pymat.search("stainless")         # → [stainless, s304, s316L, ...]
pymat.search("316")               # → [s316L, s316, ...]
pymat.search("stainless 316")     # → [s316L]   # all tokens must match
pymat.search("lyso ce saint")     # → [prelude420, ...]   # deep hierarchy
```

## Out of scope for v1

- Scoped search (`kind="grade"` / `kind="parent"`) — optional follow-up.
- Aliases / synonyms — punt.
- Levenshtein via `rapidfuzz` — substring + token is enough. Optional extra later if needed.
- Property filters (`"density > 8"`) — different API.

## Related

- build123d#1270 — motivates the shape-side lookup shorthand.
- #78 — Vis adapter-method sugar (same discoverability-without-architectural-change pattern).
- mat-vis#93 — visual-side architectural endgame; orthogonal.
