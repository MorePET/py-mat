---
type: issue
state: open
created: 2026-04-19T16:44:25Z
updated: 2026-04-19T16:44:25Z
author: bernhard-42
author_url: https://github.com/bernhard-42
url: https://github.com/MorePET/mat/issues/89
comments: 0
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-20T04:51:01.590Z
---

# [Issue 89]: [[FEATURE] Non fuzzy search](https://github.com/MorePET/mat/issues/89)

### Description

For the string assignment in build123d:

In [5]: b1 = Box(1, 1, 1)
   ...: b1.material = "Stainless 304"
I thought of using pymat.search.

I need a way to uniquely find a material.

### Problem Statement

If I want the "normal "Stainless Steel", I get back all of them, and can't easily narrow down besides filtering
```python
In [23]: m = pymat.search("Stainless Steel")

In [24]: m
Out[24]: 
[Material('stainless', ρ=8.0 g/cm³),
 Material('stainless.s303', ρ=8.0 g/cm³),
 Material('stainless.s304', ρ=8.0 g/cm³),
 Material('stainless.s316L', ρ=8.0 g/cm³),
 Material('stainless.s17_4PH', ρ=7.8 g/cm³),
 Material('stainless.s316L.passivated', ρ=8.0 g/cm³),
 Material('stainless.s316L.electropolished', ρ=8.0 g/cm³)]
```

For specif instances it works:

In [25]: m = pymat.search("Stainless Steel 304")

In [26]: m
Out[26]: [Material('stainless.s304', ρ=8.0 g/cm³)]

In [27]: m = pymat.search("Stainless Steel")

In [28]: m
Out[28]: 
[Material('stainless', ρ=8.0 g/cm³),
 Material('stainless.s303', ρ=8.0 g/cm³),
 Material('stainless.s304', ρ=8.0 g/cm³),
 Material('stainless.s316L', ρ=8.0 g/cm³),
 Material('stainless.s17_4PH', ρ=7.8 g/cm³),
 Material('stainless.s316L.passivated', ρ=8.0 g/cm³),
 Material('stainless.s316L.electropolished', ρ=8.0 g/cm³)]

### Proposed Solution

for example introduce a `fuzzy` argument with default `True`:

```python
m = pymat.search("Stainless Steel", fuzzy=False)
```

Then I can call `pymat.search("Stainless Steel", fuzzy=False)` If that comes back with one material all good, if no material comes back I can issue  `pymat.search("Stainless Steel")` to get all of them and raise a non-unique error that shows the user all valid names

### Alternatives Considered

any better idea appreciated

### Additional Context

_No response_

### Impact

_No response_

### Changelog Category

Added
