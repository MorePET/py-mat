---
type: issue
state: open
created: 2026-04-22T09:29:43Z
updated: 2026-04-22T09:29:43Z
author: bernhard-42
author_url: https://github.com/bernhard-42
url: https://github.com/MorePET/mat/issues/99
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-23T04:44:00.970Z
---

# [Issue 99]: [[BUG] to_threejs creates an int as a color which is unusual for Python](https://github.com/MorePET/mat/issues/99)

### Description

Currently `material.vis.to_threejs()["color"]` is an `int`
Typically in Python rgb colors are 3-tuples r,g,b with each value in [0,1] or css like strings `'#bfbfc4'`


### Steps to Reproduce

```python
import stainless
print(stainless.vis.to_threejs()["color"])
# 12566468
```

### Expected Behavior

```python
import stainless
print(stainless.vis.to_threejs()["color"])
# (0.7490196078431373, 0.7490196078431373, 0.7686274509803922) or "'#bfbfc4'"
```

### Actual Behavior

see above

### Environment

any

### Additional Context

_No response_

### Possible Solution

_No response_

### Changelog Category

Fixed
