---
type: issue
state: closed
created: 2026-04-15T08:28:42Z
updated: 2026-04-15T10:52:16Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/10
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-16T04:44:39.323Z
---

# [Issue 10]: [pymarkdown MD031 plugin crashes on RELEASE_PROCESS.md](https://github.com/MorePET/mat/issues/10)

## Context

While unblocking CI in #8, pymarkdown (\`v0.9.23\`) crashed with:

\`\`\`
BadPluginError encountered while scanning 'RELEASE_PROCESS.md':
(29,4): Plugin id 'MD031' had a critical failure during the 'next_token' action.
\`\`\`

MD031 is \"fenced-code-language\" / \"blanks-around-fences\" depending on version — whichever it is, the plugin itself throws, so pymarkdown can't even report a normal rule violation on this file.

## Workaround applied in #8

\`.pre-commit-config.yaml\` now excludes \`RELEASE_PROCESS.md\` (and \`TEMPERATURE_UNITS_IMPLEMENTATION.md\` which had similar issues) from pymarkdown:

\`\`\`yaml
exclude: ^(README\.md|CONTRIBUTE\.md|TESTING\.md|RELEASE_PROCESS\.md|TEMPERATURE_UNITS_IMPLEMENTATION\.md)
\`\`\`

This is a temporary mask, not a fix. The file is still part of the repo and presumably does have markdown issues worth catching.

## What to do

Options:
1. **Upgrade pymarkdown** — check if a newer \`v0.9.x\` no longer crashes on the same input. If yes, bump \`.pre-commit-config.yaml\` and remove the exclusion.
2. **Minimal repro + upstream bug report** — reduce \`RELEASE_PROCESS.md\` to a minimal markdown snippet that still crashes MD031, file upstream at https://github.com/jackdewinter/pymarkdown, and reference here.
3. **Rewrite the offending section** — around line 29, col 4 of \`RELEASE_PROCESS.md\` — to not trip the plugin, then remove the exclusion.

Option 1 is cheapest if a newer release fixes it. Otherwise 3 > 2.

## Acceptance criteria

- [ ] \`pymarkdown\` passes on \`RELEASE_PROCESS.md\` and \`TEMPERATURE_UNITS_IMPLEMENTATION.md\`
- [ ] \`.pre-commit-config.yaml\` exclude list reverted to \`^(README\.md|CONTRIBUTE\.md|TESTING\.md)\`
---

# [Comment #1]() by [gerchowl]()

_Posted on April 15, 2026 at 10:52 AM_

Fixed in #14 (merged to dev: e2128911).

Root cause: pymarkdown's MD031 *fixer* (not scanner) has a bug with fenced code blocks nested inside list items — it strips the 3-space indent, un-nesting the block. On the container runner it crashes with BadPluginError; on newer local versions it silently corrupts the file.

Workaround: `RELEASE_PROCESS.md` and `TEMPERATURE_UNITS_IMPLEMENTATION.md` rewritten in the correct form (blank line before fence, fence still at 3-space indent, fixed MD022/MD026/MD032/MD034 while in the area). Both files are now idempotent under `pymarkdown fix` + `scan`, and the pre-commit exclusion list drops back to the original three files.

The underlying pymarkdown fixer bug should still be reported upstream at https://github.com/jackdewinter/pymarkdown — if someone wants to file that, minimal repro is a fenced code block immediately after a numbered list item marker with no intervening blank line, indented 3 spaces to stay inside the list item.

