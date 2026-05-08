---
type: issue
state: open
created: 2026-05-07T11:56:26Z
updated: 2026-05-07T12:04:24Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/221
comments: 0
labels: enhancement
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-05-08T04:48:04.065Z
---

# [Issue 221]: [Vis: repr stays None even after fetch — observability of lazy state](https://github.com/MorePET/mat/issues/221)

## Source

Bernhard's mat-vis#311 — sub-bullet "Inconsistent outputs".
https://github.com/MorePET/mat-vis/issues/311

> Reported against pymat 3.10.0. **Bug persists on current dev (35681ce)** — `Vis` is a `@dataclass` with no custom `__repr__`, so the auto-generated repr keeps showing identity-time field values (which are all `None` until the user explicitly overrides them). Version line is provenance only.

## Problem

`Vis` is a lazy API: scalar fields stay `None` until `.textures` / `.to_threejs()` triggers a fetch. After fetch, the repr is **still** all-None even though the data is loaded — the user has no signal that anything happened.

## Repro

```python
v = Vis(source="gpuopen", material_id="Aluminum Brushed", tier="1k")
v
# Vis(source='gpuopen', material_id='Aluminum Brushed', tier='1k', finishes={},
#     roughness=None, metallic=None, base_color=None, ior=None, transmission=None, ...)

t = v.to_threejs()      # fetches!
t["metalness"], t["roughness"]
# (1.0, 0.4)            ← data is there

v
# Vis(source='gpuopen', material_id='Aluminum Brushed', tier='1k', finishes={},
#     roughness=None, metallic=None, base_color=None, ior=None, transmission=None, ...)
# ← still all None
print(v.metallic)
# None
```

Bernhard's expectation:

```python
v   # before fetch
# Vis(source='gpuopen', material_id='Aluminum Brushed', tier='1k', finishes={}, fetched=False)

v.textures   # triggers fetch

v   # after fetch
# Vis(source='gpuopen', material_id='Aluminum Brushed', tier='1k', finishes={},
#     roughness=0.4, metallic=1.0, base_color="#cccccc", ior=1.5, transmission=0,
#     available_textures=['color', 'normal', 'roughness'])
```

## Root cause

The `Vis` dataclass declares fields like `roughness: float | None = None` for **caller overrides**, not for cached fetched values. Cached values live in `_textures` / `_fetched` (private), and the catalog's authored scalars are read on demand via the adapter — they never populate the dataclass fields.

So the repr is technically truthful ("the user hasn't overridden these"), but for the user it reads as "nothing is loaded." Two valid framings collide.

## Options

1. **Minimal:** Repr-only change — show `fetched=True/False` flag. Don't touch field semantics.
2. **Medium:** When `_fetched=True`, the repr also shows the authored scalars from the catalog (read via the proposed `Vis.scalars` accessor — see related issue).
3. **Heavier:** Populate the dataclass fields after fetch (semantic change — overrides become indistinguishable from authored values).

## Recommendation

(1) + (2): show `fetched=True`, plus inline a `scalars=...` summary when fetched. Keeps the override/authored distinction honest while giving the user a visible signal.

## Acceptance

- [ ] Pre-fetch `repr(v)` shows `fetched=False`
- [ ] Post-fetch `repr(v)` shows `fetched=True` plus a `scalars=` summary (or `available_textures=`)
- [ ] Override semantics unchanged: explicit `v.metallic = 0.7` still surfaces in repr as the override
- [ ] No new HTTP cost (the catalog scalars are already loaded)
- [ ] **Forward verify:** re-run bernhard's literal repro from mat-vis#311 (the "Inconsistent outputs" snippet) end-to-end and confirm the post-fetch repr matches his expectation. The mat-vis#287/#288 lesson: don't trust unit tests alone for user-surface bugs.

## Related

- mat#220 (`Vis.scalars` accessor — this issue assumes it exists)
