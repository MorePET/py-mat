---
type: issue
state: open
created: 2026-05-07T20:59:25Z
updated: 2026-05-07T20:59:25Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/227
comments: 0
labels: enhancement
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-05-08T04:48:03.158Z
---

# [Issue 227]: [list_materials / by_name surface — display-name ergonomic on top of mat-vis-client.materials()](https://github.com/MorePET/mat/issues/227)

## Source

mat-vis#330 (closed; moved here): bernhard's #311 sub-bullet "Consistently support material names" — `mat_vis_client.materials("gpuopen", "1k")[:3]` returns `['0075d7cd-...', '00b064e2-...', '010c2da8-...']`. He wanted `['Red Brick Wall Weathered', 'TH: Blue Painted Planks', ...]` or a `{id: name}` dict.

mat-vis-side rationale for moving: `materials()` returning canonical IDs is structurally correct (those are what uniquely identify materials in the substrate; URL-building, ETag invalidation, content-drift gates all key off the ID). Adding `materials_named()` at the low-level client clutters its API for a consumer ergonomic that has a natural home one layer up.

## Problem (from a pymat consumer's seat)

bernhard picks materials interactively or by-name in his own code. He doesn't render UUIDs in his UI. The natural pymat surface:

```python
import pymat
# Today consumers do:
ids = mat_vis_client.get_client().materials("gpuopen", "1k")
# → uuids; bernhard then has to look up each id's mat_vis.name himself

# Proposed:
materials = pymat.list_materials("gpuopen", "1k")
# → list of (id, display_name) pairs OR dict {id: name}, designed for
#   ergonomic iteration / filtering / display
```

`Vis(source, name)` already accepts display names on construction (mat-vis#284 added the input-side resolution). This issue is the **output-side companion**.

## Proposal

Add to pymat (location TBD by maintainer — probably `pymat.vis.list_materials` to live next to `Vis`):

```python
def list_materials(
    source: str,
    tier: str | None = None,
    *,
    by: Literal["id", "name", "both"] = "name",
) -> list[str] | dict[str, str]:
    """List materials in a (source, tier).

    by="name" (default): list of display names — for UI / fuzzy
        filtering / grep.
    by="id": list of canonical IDs — same as
        mat_vis_client.materials() (the underlying programmatic key).
    by="both": dict {id: display_name} — for consumers that need to
        render names but resolve IDs (most common build123d use).
    """
```

Implementation reads `mat_vis_client.client.index(source)`, projects `entry["id"]` and `entry["mat_vis"]["name"]`, applies the tier filter, returns the requested shape.

## Why pymat and not mat-vis-client

- Single-responsibility: `materials()` at the client layer = "list of canonical IDs in the substrate at this (source, tier)". Adding a display-name variant there couples the substrate-layer API to consumer presentation choices.
- `Vis(source, name)` lives in pymat; symmetric to expose the listing surface in pymat too.
- pymat owns the consumer-facing namespace. mat-vis-client should stay focused on substrate plumbing.

## Acceptance

- [ ] `pymat.vis.list_materials("ambientcg", "1k")` returns the curated names from `entry.mat_vis.name`
- [ ] `by="both"` returns `{id: name}` dict — most useful for build123d-style UIs
- [ ] `tier=None` (post mat-vis#341) returns all materials with ≥1 tier — same semantics as `mat_vis_client.materials()`
- [ ] `Vis` consumers can do `Vis("gpuopen", name)` with any name from this listing — already works per mat-vis#284
- [ ] **Forward-verify** with bernhard's repro from mat-vis#311 ("Consistently support material names" section): listing returns the names he expects, no UUID exposure

## References

- mat-vis#330 (closed; moved here)
- mat-vis#311 (bernhard's umbrella — this is one of the surviving sub-bullets)
- mat-vis#284 (input-side: name-addressing on `Vis(source, name)`)
- mat-vis#341 (`materials(source)` with tier optional — established the parent API shape)
