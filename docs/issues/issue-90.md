---
type: issue
state: closed
created: 2026-04-20T10:50:41Z
updated: 2026-04-20T16:05:12Z
author: bernhard-42
author_url: https://github.com/bernhard-42
url: https://github.com/MorePET/mat/issues/90
comments: 6
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-21T04:41:35.020Z
---

# [Issue 90]: [[BUG] Can't download materials from GPUOpen](https://github.com/MorePET/mat/issues/90)

### Description

I want to use this material

<img width="1060" height="204" alt="Image" src="https://github.com/user-attachments/assets/7b9eab91-4795-4a2b-a92f-ed8ed7630ff6" />

1) `client.fetch_all_textures` doesn't find it
2) As a user, I might not want to use the UUID. It tells me nothing in my code.

### Steps to Reproduce

Get the UUID from the GPUOpen page's URL

https://matlib.gpuopen.com/main/materials/all?category=Metal&material=25b88a68-251a-414a-a5b5-68381adfdc5f

Here `25b88a68-251a-414a-a5b5-68381adfdc5f`

```python
In [86]: from mat_vis_client import MatVisClient
    ...: 
    ...: client = MatVisClient()
    ...: client.fetch_all_textures("gpuopen", "25b88a68-251a-414a-a5b5-68381adfdc5f")
Out[86]: {}
```

### Expected Behavior

**Best option:**

Users will select materials based on the rendering, not base on a list. Hence they will check put the GPUOpen, ... websites

```python
from mat_vis_client import MatVisClient

client = MatVisClient()
client.fetch_all_textures("gpuopen", "Aluminum Corrugated")
```

**Non preferred option:**

```python
client.fetch_all_textures("gpuopen", "25b88a68-251a-414a-a5b5-68381adfdc5f")
```

### Actual Behavior

Returns `{}`

### Environment

macos / Py 3.13

### Additional Context

_No response_

### Possible Solution

_No response_

### Changelog Category

Fixed
---

# [Comment #1]() by [bernhard-42]()

_Posted on April 20, 2026 at 11:03 AM_

To add to this
```python
In [113]: client.materials("gpuopen", "1k")[:5]
Out[113]: 
['0003d1c1-491f-47bf-b417-5ba72a5a80a5',
 '002d5911-4b55-4d73-aa86-7487a72af4d6',
 '00495957-5ee9-4359-bfaa-aea16962af28',
 '00727189-8d16-4872-b15d-620d41cb509f',
 '0097a039-5c22-49f2-93be-3f9755482f87']

In [114]: client.materials("ambientcg", "1k")[:5]
Out[114]: 
['AcousticFoam001',
 'AcousticFoam002',
 'AcousticFoam003',
 'Asphalt004',
 'Asphalt005']

In [115]: client.materials("polyhaven", "1k")[:5]
Out[115]: 
['aerial_asphalt_01',
 'aerial_beach_01',
 'aerial_beach_02',
 'aerial_beach_03',
 'aerial_grass_rock']
```

Users can't work with GPUOpen's list 

Plus, using `0003d1c1-491f-47bf-b417-5ba72a5a80a5`

<img width="1060" height="204" alt="Image" src="https://github.com/user-attachments/assets/7ab5224a-239a-45bc-aaec-6aa1cd0a1fd0" />

---

# [Comment #2]() by [bernhard-42]()

_Posted on April 20, 2026 at 11:08 AM_

And:

```python
In [123]: client.index("gpuopen")[0]
Out[123]: 
{'id': '0003d1c1-491f-47bf-b417-5ba72a5a80a5',
 'source': 'gpuopen',
 'name': '1k 8b',
 'category': 'other',
 'tags': [],
 'source_url': 'https://matlib.gpuopen.com/main/materials/all?material=0003d1c1-491f-47bf-b417-5ba72a5a80a5',
 'source_license': 'TBV',
 'available_tiers': ['1k'],
 'maps': ['color', 'normal', 'roughness'],
 'last_updated': '2023-08-07T01:59:14.969183Z',
 'texture_hashes': {'roughness': {'sha256': 'b6f96290ac3c8fcd7b467cef9ff040601f449f55432fa5a1549660d0f65c93b6',
   'size': 468154},
  'normal': {'sha256': '6d6cccec788c111e1c13e89daf31a7115c2fdc872e4829f8a5f2a8e38f98025a',
   'size': 1957762},
  'color': {'sha256': '7af979027d76e25958f4dc9996bd02c7ffc29607f1a0ace26df63d631fc58032',
   'size': 2273176}}}
```

If I paste the source URL: https://matlib.gpuopen.com/main/materials/all?material=0003d1c1-491f-47bf-b417-5ba72a5a80a5 into the browser I get 

<img width="1060" height="204" alt="Image" src="https://github.com/user-attachments/assets/28e9d824-87ca-4d26-a009-7bf280a99650" />

---

# [Comment #3]() by [gerchowl]()

_Posted on April 20, 2026 at 01:25 PM_

Two distinct things going on here — let me separate them so we triage correctly:

### 1. `fetch_all_textures("gpuopen", <uuid>)` returns `{}` — data-pipeline bug

This is a **mat-vis** bake/derive issue, not a client or py-mat bug. The gpuopen bakes have been failing recently (see e.g. mat-vis#122 `[derive-failed] ktx2 gpuopen/2k @ v2026.04.1`). The index entry exists, the textures weren't successfully staged to the release assets the client reads from → `fetch_all_textures` returns empty.

Moving the "gpuopen returns empty" half of this to mat-vis — the fix is in the bake pipeline, not here. I'll cross-link the tracking issue.

### 2. UUID-as-user-identifier UX problem — legitimate

You're right that pasting `25b88a68-251a-414a-a5b5-68381adfdc5f` from a browser URL into code is hostile UX. Two mitigations we can ship:

- **`mat-vis-client` side**: make `fetch_all_textures(source, id_or_name)` resolve `id_or_name` against the index's `name` field as a fallback when the literal `id` lookup misses. Lets you do `fetch_all_textures("gpuopen", "Aluminum Corrugated")`. Small change, additive, no breakage.
- **py-mat side**: for consumers like build123d that want a user-friendly string, the `vis.search(query=...)` call already accepts category + tags + scalar similarity. Once gpuopen is producing `name` fields consistently (see #1 above), name-based search works for gpuopen the same as it does for ambientcg.

I'll file the name-lookup enhancement on the mat-vis side and link it here. The data-pipeline fix needs to land first before either helps visibly.

Short version: code on our side isn't wrong, but the data layer it depends on is in a thin/inconsistent state right now. Sorry for the friction while the pipeline stabilizes.


---

# [Comment #4]() by [gerchowl]()

_Posted on April 20, 2026 at 03:26 PM_

Investigated — two concrete answers for you:

### What does it raise now?

**Nothing.** Silent empty dict for both "unknown id" and "in index but unbaked". That's the DX problem, filed as [mat-vis#141](https://github.com/MorePET/mat-vis/issues/141) — typed `UnknownMaterialError` vs `MaterialNotStagedError` so you can tell the failure modes apart.

### Your specific UUID `25b88a68-…`

Checked against the live mat-vis index — that UUID **is not indexed at all**. So the fetch returning `{}` is correct-but-silent; the gpuopen material you pointed at hasn't been baked into mat-vis yet (or it was baked under a different UUID). That's a data-side item to track on the mat-vis repo, not a client bug.

### Working gpuopen materials — yes, lots

You can test the pipeline with any of the 2,254 gpuopen entries that are already baked. Grab from the index:

```python
>>> from mat_vis_client import MatVisClient
>>> client = MatVisClient()
>>> ids = client.materials("gpuopen", "1k")
>>> len(ids)
2254
>>> for uuid in ids[:3]:
...     tex = client.fetch_all_textures("gpuopen", uuid, tier="1k")
...     print(uuid, sorted(tex.keys()), sum(len(v) for v in tex.values()) // 1024, "KB")
0003d1c1-491f-47bf-b417-5ba72a5a80a5 ['color', 'normal', 'roughness'] 4588 KB
002d5911-4b55-4d73-aa86-7487a72af4d6 ['color', 'normal'] 3725 KB
00495957-5ee9-4359-bfaa-aea16962af28 ['color', 'normal', 'roughness'] 5311 KB
```

All three fetched cleanly. Sampled 10/10 so it's not a fluke — the gpuopen pipeline works for the baked materials.

### The UUID-as-id UX is still bad though

You're right that pasting `0003d1c1-491f-47bf-b417-5ba72a5a80a5` from a browser URL into code is hostile. The `name` field on gpuopen entries right now is garbage (`"1k 8b"`, `"4k 16b"` — texture-resolution metadata, not semantic names). That's a metadata-quality bug on the mat-vis side (gpuopen's upstream doesn't expose clean names the way ambientcg / polyhaven do; we need a different extraction path). Tracking that separately.

Summary: you're not blocked — concrete working UUIDs exist. The silent-`{}` and the UUID-UX are both real gaps, and both have issues filed now. Sorry for the friction.


---

# [Comment #5]() by [gerchowl]()

_Posted on April 20, 2026 at 03:29 PM_

Quick addendum — the gpuopen metadata issue is now filed separately as [mat-vis#142](https://github.com/MorePET/mat-vis/issues/142). The name-extraction fix + rebake is what unblocks `vis.search(category="metal", source="gpuopen")` and the name-instead-of-UUID workflow. Two issues now tracking the py-mat#90 surface: mat-vis#141 (silent empty-dict → typed errors) and mat-vis#142 (metadata extraction).

---

# [Comment #6]() by [gerchowl]()

_Posted on April 20, 2026 at 03:38 PM_

**Correction** (after a `/falsify` review of my own triage — sorry for the noise):

#141 + #142 alone do **not** make `fetch_all_textures("gpuopen", "Aluminum Corrugated")` work. That call still fails post-fix because `fetch_all_textures`'s lookup is UUID-keyed; #142 only fixes the *index metadata* so you can browse by name, and #141 upgrades the silent `{}` to `UnknownMaterialError` for a name string. The preferred UX in this issue needs a third piece: name→UUID resolution inside the client.

Full upstream plan for v0.5.0 — HF substrate:

- **MorePET/mat-vis#141** — `UnknownMaterialError` / `MaterialNotStagedError` on `fetch_all_textures` (no more silent `{}`).
- **MorePET/mat-vis#142** — gpuopen index extractor uses real `title` / `categoryTitle` / `tags` instead of the texture-preset filename.
- **MorePET/mat-vis#143** — `fetch_all_textures` / `fetch_texture` accept `material_id` as either UUID or human-readable name. **This is the issue that unblocks the "Best option" snippet in this bug report.**
- **MorePET/mat-vis#144** — `AmbiguousMaterialError` for the collision case (two gpuopen entries sharing the same title).

#143 is the load-bearing fix for the preferred UX. #141/#142/#144 are supporting. All four labeled `priority:high` or above and attached to milestone v0.5.0.

