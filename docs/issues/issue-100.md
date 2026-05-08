---
type: issue
state: open
created: 2026-04-22T11:09:17Z
updated: 2026-05-07T14:54:05Z
author: bernhard-42
author_url: https://github.com/bernhard-42
url: https://github.com/MorePET/mat/issues/100
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-05-08T04:48:08.702Z
---

# [Issue 100]: [[FEATURE] Add properties that typically appear from baking materials of the 4 sources](https://github.com/MorePET/mat/issues/100)

### Description

Some properties like `dispersion` or `opacityMap` are not supported in py-materials or mat-vis

### Problem Statement

I baked quite some materials from GPUOpen and ambientCG and the baking code of threejs-materials creates:

- **Scalar values**
    - `color`
    - `metalness`
    - `roughness`
    - `ior`
    - `clearcoat`
    - `transmission`
    - `dispersion`
    - `thickness`
    - `specularColor`
    - `specularIntensity`
    - `clearcoatRoughness`
    - `displacementScale`

- **Textures**
    - `color`
    - `metalnes`
    - `roughness`
    - `norma`
    - `opacity`
    - `displacement`

`material.vis.to_threejs()` currently returns

- **Scalar values**
    - `color`
    - `metalness`
    - `roughness`
    - `ior`
    - `transmission`
    - `clearcoat`
    - `emissive`

- **Textures**
    - `map`
    - `metalnessMap`
    - `roughnessMap`
    - `normalMap`
    - `aoMap`
    - `displacementMap`
    - `emissiveMap`

**Missing properties:**

- `opacityMap` is missing (used e.g. for sheet metal with holes,   "name": "Sheet Metal 001",  "source": "ambientcg")
- `dispersion` is missing ("name": "Plastic (Acrylic)",  "source": "physicallybased"). The user needs to add `thickness` in order for `dispersion` being visible

**Info**
- `displacement` and `displacemantMap` are ignored in build123d since CAD tessellation do not have sufficient vertices

### Proposed Solution

Add them to py-materials (or mat-vis) and expose them with `to_threejs()`

### Alternatives Considered

_No response_

### Additional Context

_No response_

### Impact

_No response_

### Changelog Category

Added
---

# [Comment #1]() by [gerchowl]()

_Posted on May 7, 2026 at 02:54 PM_

**Routing — upstream issue.** This is the same shape of audit as the [adapter cluster](https://github.com/MorePET/mat-vis/issues/298) we filed earlier (#298 / #302 / #303 / #304 / #305): every property listed here needs both a baker change (extract from authored .mtlx) and a client-adapter change (pass through to the output dict). py-mat side is purely consumer of whatever mat-vis exposes — no point doubling the work downstream.

Filed upstream as [mat-vis #340 — Adapters: expose full MeshPhysicalMaterial PBR scalar set + opacityMap](https://github.com/MorePET/mat-vis/issues/340). Concrete proposal:

- 6 missing scalars: `thickness`, `dispersion`, `specularColor`, `specularIntensity`, `clearcoatRoughness`, `displacementScale` (per your audit)
- 1 missing texture: `opacityMap` (your sheet metal / perforated panels example)
- Two-layer fix per property (baker extraction + adapter passthrough), same pattern that closed `emissive` / `clearcoat` (#302 → on `dev`)
- Incremental — properties can land one at a time as authored data is available

Same data-side blocker as #285: baker fix is code; consumers see nothing change until substrate re-bakes and HF uploads. The work can ship in the next re-bake cycle.

Leaving open here as the downstream-tracking issue. Will close with a release-link once mat-vis-client ships these fields and py-mat picks up the new dep version. Two of the seven (`emissive`, `clearcoat`) are already on `mat-vis@dev` per #302.

Thanks for the careful field-by-field audit, @bernhard-42 — your threejs-materials output shape is the reference list this work is converging toward.

