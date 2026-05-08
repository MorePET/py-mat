---
type: issue
state: closed
created: 2026-04-19T10:52:10Z
updated: 2026-05-07T17:02:40Z
author: bernhard-42
author_url: https://github.com/bernhard-42
url: https://github.com/MorePET/mat/issues/84
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-05-08T04:48:09.677Z
---

# [Issue 84]: [[DISCUSSION] How to integrate with build123d and ocp vscode now?](https://github.com/MorePET/mat/issues/84)

### Description

I am very impressed about what you achieved in the last few days. However, I must admit I don't understand how things work any more. Tried to read read through your docs, PRs, and code, but decided asking might be better:

- Is it correct that with `mat` and `mat-vis-client` one doesn't need `threejs-materials` any more? (which is completely OK for me)
- Do we still need a `Material` class in `build123d`, or would `shape.material:pymat.Material` be sufficient (would be OK for me if materials all come from one side)
- Found `<material>.vis` with lazy texture options, but how do I chose one option (e.g. brushed) and when will the textures be loaded?
- How do I apply a material from pymat with textures to build123d now and how does `node.material.pbr_source` get set.

I am sure it is noted somewhere, but we have 3 repos and quite some PRs currently ...



### Context / Motivation

Integration into build123d

### Options / Alternatives

_No response_

### Open Questions

_No response_

### Related Issues

_No response_

### Changelog Category

No changelog needed
---

# [Comment #1]() by [gerchowl]()

_Posted on May 7, 2026 at 05:02 PM_

**Closing — substantively answered by what shipped.**

This was Bernhard's discussion-shaped issue from 18 days ago asking how to integrate py-materials with build123d / ocp_vscode. Since then:

- **Material assignment**: `shape.material = pymat["Stainless Steel 304"]` works (subscript lookup added 3.4.0, name normalization + ambiguity errors with candidates).
- **PBR adapter handoffs**: `m.vis.to_threejs()` / `m.vis.to_gltf()` / `m.vis.mtlx.export(dir)` cover Three.js, glTF 2.0 (with KHR_materials_ior + KHR_materials_transmission), and MaterialX export pipelines respectively.
- **`Vis` is officially public** (3.10.0 + 3.11.0 trailing follow-ups) — `from pymat import Vis, VisDeltas, FinishEntry, Source` works, type annotations land on the public path, field set is semver-stable.
- **Safe-derive**: `Vis.override` + `Material.with_vis` (3.7.0/3.8.0) handle the registry-singleton mutation hazard.
- **Scalar-only sources** ([#222](https://github.com/MorePET/mat/issues/222)/[#225](https://github.com/MorePET/mat/pull/225)): `Vis(source="physicallybased", material_id="X").to_threejs()` works without raising.
- **Tier validation**: `vis.tier = "99k"` raises `ValueError` with available tiers at the assignment site.

The active integration discussion lives at [build123d#1270](https://github.com/gumyr/build123d/pull/1270) (Bernhard's PR), with regular cross-references back here.

For the ongoing question of **how community-curated materials should be contributed**, see [#218](https://github.com/MorePET/mat/issues/218) — the new tracking issue.

Thanks @bernhard-42 — this discussion shaped the API direction substantially. Closing as resolved-by-shipping; happy to reopen or fork into a focused issue if specific pieces of the integration story still need clarification.

