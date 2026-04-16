---
type: issue
state: closed
created: 2026-04-15T08:28:59Z
updated: 2026-04-15T11:10:48Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/11
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-16T04:44:39.008Z
---

# [Issue 11]: [Python CI pinned to 3.12 due to cadquery-ocp + vtk wheel gap](https://github.com/MorePET/mat/issues/11)

## Context

\`.python-version\` is pinned to \`3.12\` so CI can complete \`uv sync --all-extras\`. Two transitive deps block newer Python:

- \`cadquery-ocp==7.8.1.1.post1\` (via \`build123d\`) — wheels for cp311, cp312, cp313 only
- \`vtk==9.3.1\` (via build123d tooling) — wheels for cp311, cp312 only

The tightest constraint is \`vtk\`, hence the 3.12 pin. \`pyproject.toml\` still lists \`requires-python = \">=3.11\"\` — end users on 3.13/3.14 can in principle install \`py-materials\` without the \`build123d\` extra, but \`uv sync --all-extras\` on 3.13+ will fail.

## Why this matters

- Local developers running Python 3.13/3.14 hit the same wall as CI and have to override (or give up on the \`build123d\` extra).
- When Python 3.13/3.14 become more ubiquitous this becomes a friction point.

## Options

1. **Wait for upstream wheels** — monitor vtk and cadquery-ocp release notes for cp313/cp314 support. VTK 9.4 may have them; check.
2. **Bump the transitive pins** — try \`cadquery-ocp\` newer than 7.8.1.1.post1 if one exists with cp313+ wheels (via \`build123d>=X\`).
3. **Split the \`all\` and \`build123d\` extras apart in CI** — run lint/test without \`--all-extras\`, have a separate job that installs build123d only when the Python version supports it (matrix with \`include\` conditions).
4. **Document the constraint in README** — just tell users to use 3.12 for the \`build123d\` extra.

## Acceptance criteria

- [ ] \`.python-version\` can be bumped to the latest stable (whichever is current when this is resolved) without breaking \`uv sync --all-extras\`.
- [ ] \`requires-python\` in \`pyproject.toml\` accurately reflects what actually works with all extras.
---

# [Comment #1]() by [gerchowl]()

_Posted on April 15, 2026 at 11:10 AM_

Fixed in #15 (merged to dev: 78d2fec3).

- `pyproject.toml`: environment marker `build123d>=0.7.0; python_version<'3.13'` on the build123d / all / dev extras. 3.13+ installs silently drop build123d instead of erroring on missing wheels. `Python :: 3.13` classifier added.
- `ci.yml`: new `test-matrix` job with two cells (py3.12 + --all-extras, py3.13 + --all-extras). Roll-up `test` job with `needs: [test-matrix]` preserves `Tests` as the required-status-check context, so branch rulesets didn't need updating. Individual matrix cells appear as `Tests (py3.12, all)` and `Tests (py3.13, all)`.
- `setup-env/action.yml`: new `python-version` and `uv-sync-args` inputs so matrix cells can override.

Build123d regressions stay visible: the 3.12 cell runs the full integration on every PR. When cadquery-ocp / vtk publish cp313+ wheels, the env markers can be removed.

