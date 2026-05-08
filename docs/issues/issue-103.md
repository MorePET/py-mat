---
type: issue
state: closed
created: 2026-05-04T12:32:45Z
updated: 2026-05-07T08:48:44Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/103
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-05-08T04:48:08.235Z
---

# [Issue 103]: [Vis.override: tier-only change wrongly clears _finish](https://github.com/MorePET/mat/issues/103)

**Bug.** Found by independent implementation review of 3.6.0.

\`vis.override(tier=\"2k\")\` on a Vis with \`_finish=\"polished\"\` clears \`_finish\` to \`None\`, even though tier is orthogonal to which finish-map entry was selected.

### Trigger
\`\`\`python
v = Vis(source=\"ambientcg\", material_id=\"Metal012\", tier=\"1k\",
        finishes={\"polished\": {\"source\": \"ambientcg\", \"id\": \"Metal012\"}})
v.finish = \"polished\"
v2 = v.override(tier=\"2k\")
assert v2.finish == \"polished\"  # FAILS — clears to None
\`\`\`

### Cause
\`src/pymat/vis/_model.py\` — \`override\` clears \`_finish\` whenever any of the 3 identity fields change. Should restrict to \`source\` / \`material_id\` (the fields a finish entry pins).

### Fix
Compute \`finish_invalidating = bool({\"source\", \"material_id\"} & set(deltas where value differs))\`, use that gate instead of \`identity_changing\`.
---

# [Comment #1]() by [gerchowl]()

_Posted on May 7, 2026 at 08:48 AM_

Fixed in [py-materials 3.7.0](https://github.com/MorePET/mat/releases/tag/v3.7.0). The finish-invalidating check in `Vis.override` was scoped to identity-changing fields only — `{source, material_id}` — so a tier-only change correctly preserves `_finish`. Pinned by `tests/test_vis_override.py::TestTierOnlyChangePreservesFinish`. (Also re-pinned in 3.11.0's `tests/test_vis_override.py` after the tier-validation work touched the same area.)

