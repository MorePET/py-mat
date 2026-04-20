---
type: issue
state: open
created: 2026-04-19T16:36:33Z
updated: 2026-04-19T16:36:33Z
author: bernhard-42
author_url: https://github.com/bernhard-42
url: https://github.com/MorePET/mat/issues/88
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-20T04:51:01.951Z
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
