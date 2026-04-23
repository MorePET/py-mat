---
type: issue
state: open
created: 2026-04-22T11:09:17Z
updated: 2026-04-22T11:09:17Z
author: bernhard-42
author_url: https://github.com/bernhard-42
url: https://github.com/MorePET/mat/issues/100
comments: 0
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-23T04:44:00.684Z
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
