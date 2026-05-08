---
type: issue
state: open
created: 2026-05-07T11:56:00Z
updated: 2026-05-07T12:03:57Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/220
comments: 0
labels: enhancement
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-05-08T04:48:04.489Z
---

# [Issue 220]: [Vis: scalars accessor missing — companion to .textures](https://github.com/MorePET/mat/issues/220)

## Source

Bernhard's mat-vis#311 — sub-bullet "Scalars as first class citizens".
https://github.com/MorePET/mat-vis/issues/311

> Reported against pymat 3.10.0 + mat-vis-client 0.6.4. **Bug persists on current dev (35681ce)** — there is no `scalars` accessor on `Vis`. Version line is provenance only; the fix lives in this repo regardless of release cadence.

## Problem

After fetching a material via `Vis.to_threejs()` or `Vis.textures`, there's no public accessor for the PBR scalars (roughness, metalness, ior, transmission, base_color, ...). Bernhard's expectation:

```python
v = Vis(source="gpuopen", material_id="Aluminum Brushed", tier="1k")
v.textures   # → {'color': b'...', 'normal': b'...', 'roughness': b'...'}  ✅ works
v.scalars    # → {'roughness': 0.4, 'metallic': 1.0, 'ior': 1.5, ...}     ❌ no such accessor
```

Currently the only way to read scalars after fetch is to invoke the adapter (`to_threejs()`) and pluck them out — but the adapter applies normalizations (e.g. `metallic × map → factor=1.0`) that hide the authored scalar values.

## Repro

```python
from pymat.vis import Vis
v = Vis(source="gpuopen", material_id="Aluminum Brushed", tier="1k")
v._fetched              # False
v.textures.keys()       # dict_keys(['color', 'normal', 'roughness'])  ← triggers fetch
v._fetched              # True
v.scalars               # AttributeError: 'Vis' object has no attribute 'scalars'
```

## Proposed shape

```python
@property
def scalars(self) -> dict[str, float | tuple | None]:
    """PBR scalars as authored by the baker, before adapter normalization.
    
    Same shape as the catalog's mat_vis.pbr block:
    {'roughness': float | None,
     'metalness': float | None,
     'base_color': (r, g, b) | None,
     'ior': float | None,
     'transmission': float | None,
     'specular_f0': (r, g, b) | None,
     'complex_ior': [...] | None}
    """
```

Reads from the catalog entry (already fetched as part of the index lookup; no extra HTTP). Empty / None for sources that don't author the field.

## Acceptance

- [ ] `v.scalars` returns the dict above for any successfully-fetched Vis
- [ ] Returns the **authored** values from `mat_vis.pbr.*`, not the adapter-normalized ones
- [ ] No-op (`{}`) for Vis without identity (no source/material_id set)
- [ ] Lazy: doesn't trigger texture fetch (scalars are already in the catalog)
- [ ] **Forward verify:** re-run bernhard's literal repro from mat-vis#311 (the "Scalars as first class citizens" snippet) end-to-end through `Vis` and confirm the output matches his expectation. Don't claim closed on unit tests alone — the upstream lesson from mat-vis#287/#288 is that pymat-surface verification is a separate proof.

## Out of scope

- Adapter behavior (`to_threejs()` etc.) stays unchanged — different concern.
