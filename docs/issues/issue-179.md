---
type: issue
state: closed
created: 2026-05-04T21:23:02Z
updated: 2026-05-07T08:48:54Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/179
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-05-08T04:48:05.857Z
---

# [Issue 179]: [search: fuzzy threshold too tight — heavy typos return empty](https://github.com/MorePET/mat/issues/179)

**DX gap surfaced via MCP UX testing.**

\`pymat.search(\"Stinless Stl 304\")\` returns \`[]\`. Both \`i\`s elided + \"Stl\" abbreviation. A human's intent is obvious; an agent's mistype is recoverable.

## Repro

\`\`\`python
>>> pymat.search(\"Stinless Stl 304\")
[]
>>> pymat.search(\"Stainless 304\")
[...]   # works
>>> pymat.search(\"Stnls Stl\")
[]      # fails
\`\`\`

## Fix

Inspect \`src/pymat/search.py\` — the current scorer / threshold. Two non-mutually-exclusive options:

1. Lower the score threshold for short queries (current threshold over-penalizes when \`len(query) < ~10\`).
2. Add abbreviation tolerance (\`Stl\` → \`Steel\`, \`Alu\` → \`Aluminum\`) for engineering vocabulary. Probably overkill; option 1 is enough.

## Why it matters

The MCP \`get_material\` tool already returns \`{\"error\": ..., \"did_you_mean\": [...]}\` envelopes — but the suggestion list is built from \`pymat.search\`, so an empty search makes the envelope unhelpful. Agents end up with no recovery path.

Catches the same class of UX hole as #178 (data gaps); fix is on the search side.
---

# [Comment #1]() by [gerchowl]()

_Posted on May 7, 2026 at 08:48 AM_

Fixed in [py-materials 3.9.0](https://github.com/MorePET/mat/releases/tag/v3.9.0). `pymat.search` migrated from `token in target` substring containment to `rapidfuzz.fuzz.partial_ratio` with a calibrated 75% threshold per token. Catches one- and two-character typos (`'Stinless 304'` → Stainless 304; `'6016'` → Aluminum 6061) without auto-matching arbitrary abbreviations. Pinned by `tests/test_search.py::TestTypoTolerance`. Note: a separate misfire on long random underscored tokens is tracked in 3.11.0's `tests/test_error_messages.py` xfail (candidate follow-up issue).

