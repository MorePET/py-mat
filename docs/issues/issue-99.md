---
type: issue
state: open
created: 2026-04-22T09:29:43Z
updated: 2026-05-07T11:39:20Z
author: bernhard-42
author_url: https://github.com/bernhard-42
url: https://github.com/MorePET/mat/issues/99
comments: 2
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-05-08T04:48:09.169Z
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
---

# [Comment #1]() by [gerchowl]()

_Posted on May 7, 2026 at 09:01 AM_

**Routing — upstream issue.** Verified the int-color encoding lives in `mat_vis_client.adapters.to_threejs`, not in py-mat:

```python
# mat_vis_client/adapters.py
if "color_hex" in scalars and scalars["color_hex"] is not None:
    result["color"] = _color_hex_to_int(scalars["color_hex"])
```

py-mat's [`src/pymat/vis/adapters.py`](https://github.com/MorePET/mat/blob/main/src/pymat/vis/adapters.py) is a thin wrapper that already converts the float-tuple `base_color` → `'#RRGGBB'` string before handing off (see `_rgba_to_hex`). The upstream then converts the string back to an int — that's the layer that needs to change. Per ADR-0002 *vis-owns-identity-client-exposed*, format-shape decisions (Three.js field names, color encoding, glTF schema) belong to the substrate library; py-mat shouldn't post-process the output.

Filed upstream: [mat-vis #298 — `to_threejs: 'color' should default to '#RRGGBB' string, not hex int`](https://github.com/MorePET/mat-vis/issues/298). Proposed fix: add `color_format=Literal["hex", "int", "tuple"]` kwarg with `"hex"` as the default. The Pythonic string default; lossless on the JS side (`MeshPhysicalMaterial` accepts CSS strings); round-trips through JSON; inspectable in REPLs.

py-mat consumes `mat-vis-client>=0.6.3` so this issue closes automatically on the next mat-vis-client release that ships the change. Leaving open here pending upstream — will close with a release-link comment once mat-vis-client 0.7.x lands.

Thanks for the report, @bernhard-42 — keeping this open as a tracking item rather than closing.

---

# [Comment #2]() by [gerchowl]()

_Posted on May 7, 2026 at 11:39 AM_

**Status:** mat-vis [milestone #3](https://github.com/MorePET/mat-vis/milestone/3) closed; the substrate side of the adapter parity work is complete and queued for the **mat-vis-client 0.7.0** release.

What landed (across phases 0.6.5 and 0.7.0):

| mat-vis | Effect on py-mat boundary |
|---|---|
| #298 | ``to_threejs(color_format="hex")`` is the new default — emits ``"#RRGGBB"`` string. py-mat consumers no longer get the un-Pythonic hex int from this issue. |
| #303 | Adapters accept ``metallic`` directly. py-mat can drop the ``metallic→metalness`` rename in ``_extract_scalars``. |
| #302 | ``emissive`` and ``clearcoat`` flow through all three adapters. py-mat's ``Vis.emissive`` / ``Vis.clearcoat`` no longer silently dropped. |
| #304 | NEW canonical input ``base_color_linear`` (linear RGBA float-4). py-mat's ``Vis.base_color`` can pass through as RGBA without ``_rgba_to_hex`` boundary loss. ``color_rgba`` (sRGB) and ``color_hex`` (sRGB) accepted as legacy aliases that de-gamma at the substrate boundary. |
| #305 | ``export_mtlx`` sanitizes ``material_name`` internally. py-mat can drop its boundary sanitize. |
| #317 | ``export_mtlx`` no longer drops ``color_hex`` on the scalar path. PBR-scalar-only materials (Stainless Steel, etc.) now export with a working ``<color3>`` ``diffuseColor`` on the shader. |
| ADR-0013 | The colorspace gap surfaced during review — ``to_gltf`` ``baseColorFactor`` was sRGB-as-linear (over-bright in spec-compliant renderers). 0.7.0 fixes this; values are now linear per glTF 2.0 §3.9.2. |

### Adoption guide for py-mat 0.7.0

1. Pin ``mat-vis-client>=0.7.0`` in pyproject.
2. In ``src/pymat/vis/adapters.py::_extract_scalars``:
   - Drop the ``metallic → metalness`` rename — pass ``"metallic": vis.get("metallic")`` directly.
   - Drop ``_rgba_to_hex`` — pass ``"base_color_linear": vis.get("base_color")`` directly (linear RGBA).
   - Pass ``vis.emissive`` and ``vis.clearcoat`` directly.
3. In the ``export_mtlx`` wrapper: drop the ``safe_name = mat_name.replace(" ", "_")...`` sanitize — the substrate handles it.
4. Tests: ``to_threejs(...)`` no longer needs the int-int comparison; the default is now the ``"#RRGGBB"`` string. If you have tests pinning the int form, pass ``color_format="int"`` explicitly.

ADR-0013 (full design): https://github.com/MorePET/mat-vis/blob/dev/docs/decisions/0013-adapter-color-input-and-scalar-coverage.md

Closing this issue once py-mat 0.7.0 ships with the adoption.

