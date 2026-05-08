---
type: issue
state: closed
created: 2026-05-06T18:44:27Z
updated: 2026-05-07T08:48:56Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/187
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-05-08T04:48:05.371Z
---

# [Issue 187]: [Re-export Vis from public path so downstream consumers stop importing from pymat.vis._model](https://github.com/MorePET/mat/issues/187)

Filed by gerchowl on behalf of bernhard-42's question on mat-vis#282 / build123d#1270.

## Problem

To use the `Vis` class — which is the recommended API for visual-only material handles — downstream consumers (build123d) currently have to write:

```python
from pymat.vis._model import Vis
```

`_model` is a private (underscore-prefixed) module. Importing a publicly-named class from a private module is fragile: if `_model` is renamed or split tomorrow (entirely within the rights of an underscore module), build123d breaks silently.

## Fix

One-line re-export in `pymat/vis/__init__.py`:

```python
from ._model import Vis

__all__ = [..., "Vis"]
```

…so the canonical import becomes:

```python
from pymat.vis import Vis
```

## Related

- mat-vis#282 — bernhard-42's original question
- mat#98 — referenced in #282

## Note

This is the only one of the seven open mat-vis issues from bernhard's build123d#1270 review that isn't actionable in mat-vis itself — every other concern landed in the mat-vis hotfix bundle (mat-vis PR #(this)).
---

# [Comment #1]() by [gerchowl]()

_Posted on May 7, 2026 at 08:48 AM_

Fixed in two stages: [py-materials 3.10.0](https://github.com/MorePET/mat/releases/tag/v3.10.0) (#98 / [PR #186](https://github.com/MorePET/mat/pull/186)) rewrote `Vis.__module__` to `pymat.vis` so `type()`, `repr`, IDE auto-import, and Sphinx all surface the public path. [py-materials 3.11.0](https://github.com/MorePET/mat/pull/80) (in flight, [PR #215](https://github.com/MorePET/mat/pull/215)) re-exports `Vis` / `VisDeltas` / `FinishEntry` / `Source` on top-level `pymat` so consumers using `import pymat` no longer need a second `from pymat.vis import …` line. Pinned by `tests/test_vis.py::TestPublicApiContract` and `tests/test_public_api_surface.py`.

