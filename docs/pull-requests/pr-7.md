---
type: pull_request
state: closed (merged)
branch: chore/bootstrap-vigos-convention → dev
created: 2026-04-15T07:04:05Z
updated: 2026-04-15T08:59:01Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/pull/7
comments: 0
labels: none
assignees: none
milestone: none
projects: none
merged: 2026-04-15T08:32:07Z
synced: 2026-04-16T04:44:58.766Z
---

# [PR 7](https://github.com/MorePET/mat/pull/7) chore: adopt vigOS convention + mat-rs PR gate

## Summary

First PR under the new dev/main rulesets. Bundles four housekeeping items and the new Rust PR gate.

**Commits:**
- `chore: housekeeping` — sync `mat-rs/Cargo.lock` to v0.2.0 release, bump `.vig-os` devcontainer 0.3.0 → 0.3.3, gitignore `.cursor/`
- `ci(rust): add PR gate for mat-rs crate` — cargo fmt/clippy/test on pull_request

## Context

- Branch rulesets were just applied to `main` and `dev` (see #522 on vig-os/devcontainer for the gap in the scaffold docs).
- The `mat-rs` crate previously had no PR-time CI gate — `release-rs-materials.yml` only runs on tag push, so a broken Rust change could land undetected. This PR closes that gap.
- The `Rust (mat-rs)` check will be added to the required-status-checks list in both rulesets after this PR confirms the context name.

## Test plan

- [ ] Lint & Format passes
- [ ] Tests pass
- [ ] Security Scan passes
- [ ] Dependency Review passes
- [ ] CodeQL Analysis (python) passes
- [ ] Rust (mat-rs) — `cargo fmt --check`, `cargo clippy -D warnings`, `cargo test` all pass
- [ ] CI Summary green

🤖 Generated with [Claude Code](https://claude.com/claude-code)


---
---

## Commits

### Commit 1: [bc8213c](https://github.com/MorePET/mat/commit/bc8213c09c9028d7098e54d9bb0f28657ee9d5e2) by [gerchowl](https://github.com/gerchowl) on April 15, 2026 at 08:30 AM
chore: bump devcontainer + add Rust PR-CI gate, 42 files modified (.github/workflows/ci.yml, .vig-os)
