---
type: issue
state: open
created: 2026-04-15T14:10:01Z
updated: 2026-04-15T14:10:01Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/31
comments: 0
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-16T04:44:38.493Z
---

# [Issue 31]: [Bump pymarkdown pre-commit rev when v0.9.37+ ships (revert #10 workaround)](https://github.com/MorePET/mat/issues/31)

## Context

Issue #10 was closed with a **workaround**, not a root-cause fix. The root cause is an upstream bug in `pymarkdown`'s MD031 fixer when a fenced code block is nested inside a list item — it strips the 3-space indent instead of adding the required blank lines, which either crashes the fixer or silently corrupts the file.

Upstream tracking: [`jackdewinter/pymarkdown#1568`](https://github.com/jackdewinter/pymarkdown/issues/1568) — labeled `waiting for issue fix verification`. Two fix PRs have already been merged to `main`:

- [`jackdewinter/pymarkdown#1581`](https://github.com/jackdewinter/pymarkdown/pull/1581) (merged 2026-04-07)
- [`jackdewinter/pymarkdown#1583`](https://github.com/jackdewinter/pymarkdown/pull/1583) (merged 2026-04-10)

**But they haven't been released yet.** Latest PyPI release as of filing is `pymarkdownlnt v0.9.36` (2026-03-16), predating both fix PRs. Our `.pre-commit-config.yaml` currently pins to `v0.9.23` (`f93643d339dfee2a1022e7b05e8b5a281bfac553`).

## What this issue tracks

When `pymarkdown` ships a release containing the two fix PRs (likely `v0.9.37` or whichever number comes next), do the following:

1. **Bump the pre-commit rev** in `.pre-commit-config.yaml`:
    ```yaml
    - repo: https://github.com/jackdewinter/pymarkdown
      rev: <SHA of the new tagged release>  # bump from v0.9.23
      hooks:
        - id: pymarkdown
          ...
    ```

2. **Verify the fix** by reverting the workaround from #10 and re-running `pymarkdown fix RELEASE_PROCESS.md`. Specifically, restore the original form where fenced code blocks are nested directly inside the list items (without the blank line between the step text and the fence):
    ```markdown
    4. **Push everything:**
       \`\`\`bash
       git push origin main --tags
       \`\`\`
    ```
    and confirm the new `pymarkdown fix` handles it cleanly without crashing or corrupting the indentation.

3. If the fix works on our exact repro, **revert the workaround rewrite** of `RELEASE_PROCESS.md` (and `TEMPERATURE_UNITS_IMPLEMENTATION.md` if applicable). Git history: commit `7b67af3` from PR #14.

4. If the fix does **not** cover our specific case, **comment on `jackdewinter/pymarkdown#1568`** with our exact minimal repro. Their reporter's example was indented-blockquote nesting; ours is numbered-list-item nesting. These may or may not be covered by the same fix.

5. **Close this issue** once the rev bump + revert land on `dev`.

## Why this is worth tracking

- The current `RELEASE_PROCESS.md` is rewritten purely to appease the buggy fixer. The "correct" markdown form is not the one we're shipping, which is a small documentation-quality regression.
- Our `pymarkdown` rev is pinned to `v0.9.23` (2+ years old). Even ignoring the MD031 fix, bumping to the latest release picks up whatever other improvements / security fixes have accumulated.
- The workaround is a maintenance tax: every time we edit `RELEASE_PROCESS.md`, we have to remember the non-obvious formatting constraint.

## Blocked on

Upstream release cut. No ETA — `jackdewinter/pymarkdown` averages one release per month based on the release history, so expect `v0.9.37` within ~4 weeks of the fix merges (which landed 2026-04-07 and 2026-04-10). Realistically mid-to-late April 2026 or early May.

## Refs

- #10 (closed — the workaround)
- #14 (the PR that rewrote `RELEASE_PROCESS.md` and `TEMPERATURE_UNITS_IMPLEMENTATION.md`)
- [`jackdewinter/pymarkdown#1568`](https://github.com/jackdewinter/pymarkdown/issues/1568) (upstream bug)
