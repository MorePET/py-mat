---
type: issue
state: open
created: 2026-04-15T13:31:52Z
updated: 2026-04-15T13:31:52Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/27
comments: 0
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-16T04:44:38.736Z
---

# [Issue 27]: [Adopt vig-os downstream release automation (prepare/release/promote)](https://github.com/MorePET/mat/issues/27)

## Context

`MorePET/mat` currently uses a ~50-line simple `release.yml` inherited from before the vigOS bootstrap: `on: push: tags: [v*]` → `uv build` → `pypa/gh-action-pypi-publish` → `gh release`. It works but doesn't match the vigOS downstream convention and doesn't support RC / candidate releases, draft-first GitHub Releases, or automated CHANGELOG date finalization.

The current session shipped release 2.1.0 using option A: the vigOS **branching pattern** (`release/X.Y.Z` branch from dev → PR to main → tag → publish via our simple workflow). That works for single releases but is manual. This issue tracks bringing in the full vigOS automation so future releases use `just prepare-release X.Y.Z` / `just finalize-release X.Y.Z` / `just promote-release X.Y.Z`.

## Source

All files live in `vig-os/devcontainer/assets/workspace/.github/workflows/`:

| File | Size | Purpose |
|---|---|---|
| `prepare-release.yml` | 14 KB | `workflow_dispatch`, freezes CHANGELOG, creates `release/X.Y.Z`, opens draft PR to main |
| `release.yml` | 8 KB | orchestrator, `workflow_dispatch` with `release_kind` (candidate / final) |
| `release-core.yml` | 21 KB | `workflow_call`, version checks + CHANGELOG validation |
| `release-extension.yml` | 1.4 KB | `workflow_call`, project-owned hook for custom publish logic |
| `release-publish.yml` | 9 KB | `workflow_call`, creates git tag + draft GitHub Release |
| `promote-release.yml` | 16 KB | `workflow_dispatch`, publishes draft, merges release → main, best-effort cleanup |

Total: ~70 KB of workflow YAML.

Upstream docs: [`docs/RELEASE_CYCLE.md`](https://github.com/vig-os/devcontainer/blob/main/docs/RELEASE_CYCLE.md), [`docs/DOWNSTREAM_RELEASE.md`](https://github.com/vig-os/devcontainer/blob/main/docs/DOWNSTREAM_RELEASE.md), [`docs/CROSS_REPO_RELEASE_GATE.md`](https://github.com/vig-os/devcontainer/blob/main/docs/CROSS_REPO_RELEASE_GATE.md).

## Scope of work

1. **Port the 6 workflow files** from the upstream template. Some will need adjustments:
    - `release-extension.yml` should be customized to do our **PyPI publish** (migrate the logic from our current `release.yml`).
    - `release.yml` (upstream) replaces our current simple `release.yml`. Our old file moves to `release-extension.yml`.
    - The upstream files use `retry` CLI from the vigOS devcontainer image in some places — we need either to replace with shell `for i in $(seq ...)` retries or to skip those retry wrappers (same constraint we hit with `sync-main-to-dev.yml`).

2. **Write `release-extension.yml`** with PyPI publish logic:
    - `uv build`
    - `pypa/gh-action-pypi-publish` via OIDC trusted publisher (already configured)
    - Attach wheel + sdist to the draft GitHub Release

3. **Add `justfile` recipes**:
    - `prepare-release X.Y.Z` → `gh workflow run prepare-release.yml --ref dev -f version=X.Y.Z`
    - `publish-candidate X.Y.Z` → `gh workflow run release.yml --ref release/X.Y.Z -f release_kind=candidate`
    - `finalize-release X.Y.Z` → `gh workflow run release.yml --ref release/X.Y.Z -f release_kind=final`
    - `promote-release X.Y.Z` → `gh workflow run promote-release.yml --ref release/X.Y.Z -f version=X.Y.Z`

4. **Configure branch ruleset for `release/**`**: similar to `dev`/`main`, require PR + strict status checks, bypass for `commit-action-bot` + `vig-os-release-app` + admins.

5. **Enable immutable releases** in repo settings (manual step, can't be automated via API afaik — needs to be documented as part of the adoption).

6. **Update `RELEASE_PROCESS.md`** to describe the new flow: `prepare → review → candidate → finalize → promote`.

7. **Verify the release secrets** we already have (`COMMIT_APP_*`, `RELEASE_APP_*`) cover everything the new workflows need. Expected yes, since they're declared required in `DOWNSTREAM_RELEASE.md`, but worth double-checking.

## Considerations

**Candidate releases on PyPI**: PyPI does support pre-releases (`X.Y.Zrc1`) but they're less commonly used. Our `release-extension.yml` will need to handle the distinction — candidates either publish to TestPyPI, or publish as pre-releases on PyPI, or are skipped entirely (git tag + draft GitHub Release only, no PyPI push until final). The vigOS upstream uses candidates heavily for container image validation; a pure-Python library may want a lighter candidate story.

**`retry` CLI dependency**: upstream's sync-issues and sync-main-to-dev use `retry --retries 3 -- gh api ...` wrappers that only work inside the devcontainer image. We already dealt with this for `sync-main-to-dev.yml` in #16 by just removing the wrapper. Same decision likely applies for the release workflows: either remove retries or reimplement in shell.

**`ci.yml` drift**: upstream's `ci.yml` is container-based. We intentionally diverged from it in #23 (see that PR body). This issue does not re-open that decision; the release workflows stay host-runner.

**Coordination with the current simple `release.yml`**: the existing file is at `.github/workflows/release.yml` and triggers on tag push. When we land the vigOS version, we need to either delete the old file (the new `release.yml` will replace it) or rename it first to avoid conflict. Plan: migrate the tag-push PyPI logic into `release-extension.yml`, delete the old `release.yml`, land the new orchestrator as `release.yml`.

## Blocked on / not blocked on

Not blocked on anything external. Blocked on someone (me / @gerchowl) having ~1-2 hours of focused work to land the port + verify end-to-end.

## Acceptance criteria

- [ ] 6 workflow files present under `.github/workflows/`
- [ ] `release-extension.yml` publishes to PyPI for final releases
- [ ] `just prepare-release X.Y.Z` + `just finalize-release X.Y.Z` + `just promote-release X.Y.Z` all work end-to-end
- [ ] A dry-run release of `v2.2.0-rc1` (candidate) succeeds without publishing to PyPI
- [ ] Required status check contexts on rulesets updated if new ones appear
- [ ] `RELEASE_PROCESS.md` rewritten for the new flow
- [ ] Old simple `release.yml` removed
- [ ] Release secrets verified

## Refs

- #23 (template refresh — the same "partial backport vs full upstream" tradeoff applies here)
- #16 (sync-main-to-dev merge-tree fix — precedent for removing `retry` wrapper dependency)
- Upstream `vig-os/devcontainer`
