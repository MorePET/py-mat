---
type: issue
state: closed
created: 2026-04-19T16:36:33Z
updated: 2026-04-20T15:53:04Z
author: bernhard-42
author_url: https://github.com/bernhard-42
url: https://github.com/MorePET/mat/issues/88
comments: 3
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-21T04:41:35.651Z
---

# [Issue 88]: [[BUG] Materials found by search lack the vis properties except the first one](https://github.com/MorePET/mat/issues/88)

### Description

For the string assignment in build123d:

```python
In [5]: b1 = Box(1, 1, 1)
   ...: b1.material = "Stainless 304"
```

I thought of using `pymat.search`. 



### Steps to Reproduce

see below

### Expected Behavior

every material found comes with default vis properties

### Actual Behavior

Unfortunately, only the first in a material chain provides it:

```python
In [18]: m = pymat.search("Stainless Steel")

In [19]: m
Out[19]: 
[Material('stainless', ρ=8.0 g/cm³),
 Material('stainless.s303', ρ=8.0 g/cm³),
 Material('stainless.s304', ρ=8.0 g/cm³),
 Material('stainless.s316L', ρ=8.0 g/cm³),
 Material('stainless.s17_4PH', ρ=7.8 g/cm³),
 Material('stainless.s316L.passivated', ρ=8.0 g/cm³),
 Material('stainless.s316L.electropolished', ρ=8.0 g/cm³)]

In [20]: m[0]
Out[20]: Material('stainless', ρ=8.0 g/cm³)

In [21]: m[0].vis
Out[21]: Vis(source='ambientcg', material_id='Metal012', tier='1k', finishes={'brushed': {'source': 'ambientcg', 'id': 'Metal012'}, 'polished': {'source': 'ambientcg', 'id': 'Metal049A'}, 'dirty': {'source': 'ambientcg', 'id': 'Metal049B'}}, roughness=0.3, metallic=1.0, base_color=(0.75, 0.75, 0.77, 1.0), ior=None, transmission=0.0, clearcoat=None, emissive=None)

In [22]: m[1].vis
Out[22]: Vis(source=None, material_id=None, tier='1k', finishes={}, roughness=None, metallic=None, base_color=None, ior=None, transmission=None, clearcoat=None, emissive=None)
```

### Environment

any

### Additional Context

_No response_

### Possible Solution

_No response_

### Changelog Category

Fixed
---

# [Comment #1]() by [bernhard-42]()

_Posted on April 20, 2026 at 11:12 AM_

I currently use

```python
        # Find the visualization properties of the parent
        vis = None
        if mat.vis.source is not None:
            vis = mat.vis
        else:
            parent = mat.parent
            while parent:
                if parent.vis.source is not None:
                    vis = parent.vis
```

but would expect this to be done by py-materials

---

# [Comment #2]() by [gerchowl]()

_Posted on April 20, 2026 at 01:25 PM_

Confirmed and agreed — grades should inherit the parent's `vis` by default. The loader currently deep-copies `self.properties` for each child but **doesn't copy `self._vis`**, so a grade without its own `[vis]` TOML section lands with an empty `Vis()`. That's exactly the inconsistency you're working around.

Fix is small and local — in `src/pymat/loader.py`, where we already carry inherited properties into each child, mirror that for vis when the TOML grade doesn't specify its own section. TOML-specified grade vis still overrides (e.g. `stainless.s316L.electropolished` can point at a different `source/material_id`), same semantics as property inheritance does today.

Your workaround walking the parent chain is what library code will do internally — you shouldn't need to carry it in build123d. Shipping this in the next py-mat patch release. Will close this issue on that merge and ping here so you can drop the workaround.


---

# [Comment #3]() by [gerchowl]()

_Posted on April 20, 2026 at 03:53 PM_

Fixed in #96, shipping in 3.4.0 (tag pushed, release.yml firing now). Grades inherit parent vis via deep-copy at load time — no more manual parent-chain walks needed. Your workaround can be deleted. Merge verified end-to-end via the new `examples/build123d_integration.py` (cell-style, runs as a pytest in CI).

