---
type: issue
state: closed
created: 2026-04-19T10:33:14Z
updated: 2026-04-19T10:44:47Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/78
comments: 0
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-20T04:51:03.069Z
---

# [Issue 78]: [Vis.to_gltf() / .to_threejs() / .export_mtlx() method sugar](https://github.com/MorePET/mat/issues/78)

## Summary

Add method-form sugar on `Vis` for the adapter functions, so `m.vis.<TAB>` surfaces the available output formats. Zero architectural change — the methods are thin delegates to the existing module-level `pymat.vis.to_gltf()` / `to_threejs()` / `export_mtlx()` functions.

## Motivation

Today the only way to get a glTF material dict from a Material is `pymat.vis.to_gltf(m)`. Module-level functions are the right shape architecturally (they're transformations, not behaviors — see [ADR-0002](docs/decisions/0002-vis-owns-identity-client-exposed.md) and the #74 PR-thread discussion), but they hide from IDE tab-completion on a `.vis` instance. Downstream consumers — notably the [build123d#1270](https://github.com/gumyr/build123d/pull/1270) Materials class PR — would benefit from `m.vis.to_gltf()` as a discoverable idiom.

## What to ship

- `Vis.to_threejs()` — returns same dict as `pymat.vis.to_threejs(material)`.
- `Vis.to_gltf(*, name: str | None = None)` — same output; `name=` fills the glTF material `name` field when called on a standalone `Vis`.
- `Vis.export_mtlx(out, *, name=None)` — same as the module-level.
- Polymorphic adapters: `to_gltf(obj)` and friends accept either a `Material` or a `Vis` (duck-typed via the `.vis` attribute). Backward-compatible.

## What NOT to do

- **No back-reference from Vis → Material.** The polymorphic adapter path avoids that. Vis stays a pure payload dataclass.
- **No Material-level methods.** `material.to_gltf()` would violate the ADR-0002 rule that `material.vis.*` owns visual concerns.
- **No new behavior.** Pure discoverability sugar. If method form and module-level form ever diverge, something has gone wrong.

## Forward-compat note

If [mat-vis#TBD](https://github.com/MorePET/mat-vis/issues) (a `VisAsset` payload object in `mat-vis-client`) lands later, the py-mat methods stay in place — their body just re-points from the module-level function to `self._asset.to_gltf()`. No downstream churn.

## Tests to add

- `to_threejs(m) == to_threejs(m.vis) == m.vis.to_threejs()` — three paths agree.
- `to_gltf(m) == to_gltf(m.vis, name=m.name) == m.vis.to_gltf(name=m.name)`.
- Vis-standalone without `name=` → empty-string name field (opt-in).
- Round-trip `export_mtlx` via both module-level and method form.

## Closes

- (this issue)

## Related

- build123d#1270 — the downstream PR that motivates the discoverability push.
- mat-vis#TBD — the architecturally-cleaner `VisAsset` direction that this doesn't preclude.
