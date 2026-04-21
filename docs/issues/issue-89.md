---
type: issue
state: closed
created: 2026-04-19T16:44:25Z
updated: 2026-04-20T16:22:01Z
author: bernhard-42
author_url: https://github.com/bernhard-42
url: https://github.com/MorePET/mat/issues/89
comments: 4
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-21T04:41:35.346Z
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
---

# [Comment #1]() by [bernhard-42]()

_Posted on April 20, 2026 at 10:52 AM_

In the meantime after code inspection I use

```python
            all_materials = pymat.load_all()
            material_name_lut = {v.name: v for k, v in all_materials.items()}

            mat = all_materials.get(material)
            if mat is None:
                mat = material_name_lut.get(material)
            if mat is None:
                raise ValueError(f"Material with key or name {material} does not exist")
```

Important feature:

The user should be able to select a material with the material id (`stainless`)  or its name (`Stainless Steel`)

Is this the correct way?

---

# [Comment #2]() by [gerchowl]()

_Posted on April 20, 2026 at 01:25 PM_

Agreed — exact lookup is a real gap. For the "give me the one that matches" case, fuzzy is the wrong default.

Shipping two things together since they're different concerns:

1. **`pymat.search(query, *, exact=False)`** — when `exact=True`, the query must equal either the registry key or `Material.name` (case-insensitive). Returns the same ranked list (possibly 0 or 1 entry), keeping the list-returning contract consistent.

2. **`pymat.get(name_or_key) -> Material`** — single-result lookup, raises on not-found, raises on ambiguity. That matches your comment "select a material with the material id (`stainless`) or its name (`Stainless Steel`)" and fits a one-liner like `b1.material = pymat.get("Stainless Steel 304")` on the build123d side without needing `[0]` indexing or ambiguity handling at the call site.

Signature sketch:

```python
pymat.search("Stainless")                # fuzzy, list
pymat.search("Stainless Steel", exact=True)   # exact, still list (len 0 or 1)
pymat.get("Stainless Steel 304")         # → Material, raises if not unique or missing
pymat.get("stainless")                   # key also works
```

Ships in the same patch release as #88. Will close here when merged.


---

# [Comment #3]() by [gerchowl]()

_Posted on April 20, 2026 at 03:53 PM_

Fixed in #96, shipping in 3.4.0. Summary:

- `pymat["Stainless Steel 304"]` / `pymat["s316L"]` / `pymat["304"]` — subscript lookup, key/name/grade targets, NFKC + case + whitespace normalization, raises with candidate list on miss/ambiguity.
- `pymat.search(q, exact=True)` — list-returning variant (now matches grade too).
- `in` operator works (`"s304" in pymat`).
- Your `material_name_lut` workaround can be dropped.

---

# [Comment #4]() by [bernhard-42]()

_Posted on April 20, 2026 at 04:22 PM_

Thanks!

