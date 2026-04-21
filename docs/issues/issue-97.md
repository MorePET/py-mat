---
type: issue
state: open
created: 2026-04-20T17:41:59Z
updated: 2026-04-20T18:05:16Z
author: bernhard-42
author_url: https://github.com/bernhard-42
url: https://github.com/MorePET/mat/issues/97
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-21T04:41:34.660Z
---

# [Issue 97]: [[FEATURE] Provide interolate_color for non PBR object colors in CAD](https://github.com/MorePET/mat/issues/97)

### Description

It would be nice if for a given vis material a simple color representation could be provided

```python
mat = pymat.Material(...)
color = mat.vis.interploate_color()
```

threejs_materials currently provides it, but it would also be nice for py-materials, I'd say.


### Problem Statement

see above

### Proposed Solution

If there is no color `map` then return `base_color`
If there is a color `map` then do interpolate the color map
If both exist, multiply base_color with map and interpolate the result

Maybe like this (pseudo code):

```python
def _srgb_to_linear(c: float) -> float:
    """Convert a single sRGB component to linear RGB (0-1)."""
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4

def _interpolate_texture(color_map: bytes, as_srgb:True) -> tuple[float, float, float]:
    img = PILImage.open(BytesIO(color_map)).convert("RGB")
    avg = img.resize((1, 1), PILImage.Resampling.LANCZOS).getpixel((0, 0))
    if as_srgb:
        r, g, b = (_srgb_to_linear(c / 255.0) for c in avg[:3])
    else:
        r, g, b = [c / 255 for c in avg[:3]]
    return (r, g, b)

class Vis:
    ...
    def interpolate_color(self):
        if <has color map>:
            return _interpolate_texture(texture)
        else:
            returen <base_color>
```

This would allow the user to set `shape.color = shape.material.vis.interpolate_color()` or even let build123d do it automatically.


### Alternatives Considered

_No response_

### Additional Context

_No response_

### Impact

_No response_

### Changelog Category

Added
---

# [Comment #1]() by [bernhard-42]()

_Posted on April 20, 2026 at 06:05 PM_

fixed the PIL code example

