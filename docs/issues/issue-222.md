---
type: issue
state: closed
created: 2026-05-07T11:56:53Z
updated: 2026-05-07T16:05:06Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/222
comments: 2
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-05-08T04:48:03.615Z
---

# [Issue 222]: [Vis: graceful handling of scalar-only sources (physicallybased / 'tier=None')](https://github.com/MorePET/mat/issues/222)

## Source

Bernhard's mat-vis#313 + mat-vis#311 sub-bullet "Support physicallybased.info" + his comment in mat-vis#281:
> some materials expect `tier=None`. Need to find out how to work with this

https://github.com/MorePET/mat-vis/issues/313  
https://github.com/MorePET/mat-vis/issues/281#issuecomment-4390009366

> Reported against pymat 3.10.0 + mat-vis-client 0.6.4. **Bug persists on current dev (35681ce)** — `_model.py:185` still has `tier: str = "1k"` and the textures path raises before the scalar-only short-circuit can kick in. Version line is provenance only.

## Problem

`Vis` defaults `tier="1k"` (`_model.py:185`). For scalar-only sources (`physicallybased`), no `1k` tier exists — the catalog uses `tier="scalar"` and there are no textures. Result: `MaterialNotStagedError` for every physicallybased material accessed via `Vis`.

## Repro

```python
from pymat.vis import Vis
v = Vis("physicallybased", "Aluminum")    # tier defaults to "1k"
v.to_threejs()
# MaterialNotStagedError: ... tier '1k' ...
```

Even passing the right tier explicitly is broken because of an upstream mat-vis bug (see "Cascade" below).

## Two intertwined problems

1. **Default-tier mismatch (this repo):** `Vis` should detect scalar-only sources and use `tier="scalar"` (or a `None` sentinel) automatically. Today the user must know the source's tier vocabulary up front.

2. **Catalog-side bug (mat-vis):** `mat-vis-client.materials("physicallybased", "scalar")` returns `[]` because every `physicallybased` catalog entry has `available_tiers=[]`. Fix is in mat-vis (`bake_scalar_source` to populate `available_tiers=["scalar"]`). Will be filed separately on mat-vis. **Both fixes need to land for bernhard's repro to pass; this issue tracks the pymat half.**

## Proposed fix in py-mat

When constructing `Vis(source, material_id)` without an explicit tier:
- Look up the source's manifest entry; if it advertises `scalar` and no textured tiers, default `tier="scalar"`.
- Otherwise default `tier="1k"` (current behavior).

Alternatively (cleaner): make `tier` resolve at fetch time rather than construction time, so an `unset` tier picks the source's "preferred" tier per-source. Avoids the mismatch by design.

For the `textures` accessor: when `tier="scalar"` (or the source carries no textures at this tier), return `{}` instead of raising. Adapter (`to_threejs()`) already handles texture-less materials per the mat-vis-client #288 fix.

## Acceptance

- [ ] `Vis("physicallybased", "Aluminum").to_threejs()` returns a valid scalar-only material dict (no exception)
- [ ] `Vis("physicallybased", "Aluminum").scalars` (per mat#220) returns the authored PBR
- [ ] `Vis("physicallybased", "Aluminum").textures` returns `{}`
- [ ] No regression on textured sources (`Vis("gpuopen", "Aluminum Brushed", "1k")` unchanged)
- [ ] **Forward verify after mat-vis fix lands:** re-run bernhard's exact repro from mat-vis#313 end-to-end through `Vis` and confirm output. The mat-vis-side `bake_scalar_source` fix MUST be on the substrate the client reads (DEFAULT_TAG-pinned) before this acceptance can be validated. Don't claim closed on unit tests alone.

## Cascade / related

- mat#220 (`Vis.scalars` accessor — needed to read the result)
- mat-vis#313 (the user-visible bug; needs both fixes — pymat-side + mat-vis catalog fix)
- mat-vis-side fix: `bake_scalar_source` should populate `available_tiers=["scalar"]` — being filed as separate mat-vis issue.
---

# [Comment #1]() by [gerchowl]()

_Posted on May 7, 2026 at 01:51 PM_

## Cross-link: mat-vis side update

mat-vis#338 (just opened) ships the **data-layer fix** that resolves the cascade you depend on: `physicallybased` catalog entries now declare `available_tiers=["scalar"]` (was `[]`). After it lands and a re-bake hits the substrate, `mat_vis_client.materials("physicallybased", "scalar")` will return 86 ids instead of `[]`.

For the **API-layer DX** concern (`tier="scalar"` is a leaky sentinel; user shouldn't have to know it), I filed mat-vis#339 separately:
- https://github.com/MorePET/mat-vis/issues/339 — `tier` becomes optional on `MatVisClient.materials`; auto-defaults to `"scalar"` for scalar-only sources.

Same DX concern lives at the `Vis` constructor surface here in mat#222 (`tier="1k"` default). Once mat-vis#339 lands the client-side ergonomic, the natural shape for pymat is:

```python
Vis("physicallybased", "Aluminum")     # tier omitted → client decides scalar default
Vis("physicallybased", "Aluminum", tier=None)   # explicit "use source default"
```

So mat#222 can wait for mat-vis#339 to land first, then mirror the same default semantics on the `Vis` side. OR: mat#222 ships its own `scalar`-source detection independently (the underlying client call still works with tier="scalar" today after #338 lands).

Either way, **all three layers must coordinate** for bernhard's mat-vis#313 repro to succeed end-to-end:
1. mat-vis#338 — catalog has `available_tiers=["scalar"]` ← landing first
2. mat-vis#339 — client `tier` optional ← optional but DX-improving
3. mat#222 — pymat `Vis` doesn't default `tier="1k"` for scalar sources ← required for bernhard's repro

Acceptance for bernhard's repro can't be claimed until all three are present and a substrate cut carries them.

---

# [Comment #2]() by [gerchowl]()

_Posted on May 7, 2026 at 03:01 PM_

## mat-vis client half shipped

mat-vis#341 just landed. `MatVisClient.materials(source, tier=None)` now hides the `"scalar"` sentinel:

```python
client.materials("physicallybased")     # → 86 ids (no "scalar" needed)
```

Combined with mat-vis#338 (catalog `available_tiers=["scalar"]`), the **mat-vis side of the cascade is complete** for bernhard's #313 repro. The next-released `mat-vis-client` (target: 0.7.0 per ADR-0013 line) will carry both fixes.

So mat#222's pymat-side fix is now the **only blocker** between bernhard and `Vis("physicallybased", "Aluminum").to_threejs()` succeeding. After mat#222 lands AND a substrate cut publishes the corrected physicallybased catalog to `gerchowl/mat-vis` (currently still on tst), the literal repro from bernhard's #313 succeeds end-to-end with no API or substrate changes needed downstream of pymat.

```python
# Full chain of fixes that lights up bernhard's repro:
# - mat-vis#338: catalog data correct (LANDED)
# - mat-vis#341: client API hides sentinel (LANDED)
# - mat#222:    pymat Vis detects scalar source (THIS ISSUE)
# - prod cut:   substrate carries the fixes (PENDING; tst already verified)
```

The forward-verify acceptance criterion on this issue ("re-run bernhard's repro through pymat after substrate cut") is now mechanically achievable as soon as the pymat-side change ships.

