---
type: issue
state: closed
created: 2026-05-04T12:33:09Z
updated: 2026-05-07T08:48:48Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/105
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-05-08T04:48:07.283Z
---

# [Issue 105]: [test: missing override coverage (adapter, tier, finishes=, None reset, TOML round-trip)](https://github.com/MorePET/mat/issues/105)

Coverage gaps flagged by independent review of \`tests/test_vis_override.py\`. Top 5 ranked:

1. **Adapter round-trip.** \`pymat.vis.to_threejs(v.override(roughness=0.6))\` carries the new value. Same for \`to_gltf\` / \`export_mtlx\`. Untested — would silently regress.
2. **\`tier=\` change clears \`_finish\`.** Pins #103 — currently no test exercises tier-only identity change with finish set.
3. **\`override(finishes={...})\` map replacement + \`finish=\` resolves against new map.** Whole code path unpinned.
4. **Scalar \`None\` reset semantics.** \`override(roughness=None)\` — allowed-and-resets vs. rejected? Behavior undocumented and untested.
5. **TOML round-trip.** Load → override → serialize → reload → equality. Catches loader/serializer drift.

Plus loose assertions to tighten:
- \`test_typo_raises_typeerror\` matches just \`\"roughnes\"\` substring; doesn't pin the \"Valid keys\" hint.
- \`TestRegistryMutationHazardFixed\` couples to TOML having a \`polished\` finish with different \`material_id\` — breaks if TOML changes. Move to a fixture-built Vis.

Block #103 + #104 fixes on these tests landing first (TDD).
---

# [Comment #1]() by [gerchowl]()

_Posted on May 7, 2026 at 08:48 AM_

Substantively addressed across [3.7.0](https://github.com/MorePET/mat/releases/tag/v3.7.0), [3.8.0](https://github.com/MorePET/mat/releases/tag/v3.8.0), and [3.11.0](https://github.com/MorePET/mat/pull/80) (in flight). `tests/test_vis_override.py` now pins: tier-only change preserves `_finish`, finishes= deep-copy, adapter pass-through, None reset, identity invalidation. 3.11.0 adds `tests/test_consumer_journey.py` and `tests/test_public_api_surface.py` covering the override surface from the consumer perspective. ~170 new contract tests overall.

