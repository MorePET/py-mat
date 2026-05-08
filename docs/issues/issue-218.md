---
type: issue
state: open
created: 2026-05-07T11:29:30Z
updated: 2026-05-07T17:03:47Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/218
comments: 1
labels: question
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-05-08T04:48:04.888Z
---

# [Issue 218]: [[DISCUSSION] Contribution pathway for community-curated materials/grades](https://github.com/MorePET/mat/issues/218)

## The question

py-mat 3.11.0 ships ~80 curated materials with `_sources` provenance and a licensing gate. The long tail of engineering materials is vast — every CAD user we don't ship is a user who needs a path to define their own. Today there are three plausible modes, and we don't yet have an opinion on the right default.

1. **Personal config** — `Material(name="MyAlloy", density=...)` ad-hoc in the user's own script. Zero ceremony; no provenance; no shared correctness.
2. **Per-project / per-vendor TOML** — committed to the user's repo, loaded via `pymat.load_toml(path)`. Per-team curation; provenance preserved; users pay the schema cost. (Existing API, undocumented as the recommended pattern.)
3. **Upstream PR** — material added to `src/pymat/data/<category>.toml` with citations + license, reviewed against `docs/data-policy.md`. Everyone gets it; highest friction.

## What I'd like your read on, @bernhard-42

Three things, where build123d's user-base shape is the strongest signal:

1. **What's the realistic split?** Of build123d users who reach for `shape.material = ...`, how many would land at (a) ad-hoc, (b) per-team TOML, (c) upstream PR? Order-of-magnitude is enough.
2. **Is the schema bar a barrier for the long tail?** A user who just wants `density` for `shape.mass` (your Level-2 ergonomic) faces the full TOML schema today. Is a lighter "drive-by" path worth building?
3. **Is the licensing/provenance gate (citation + license per property) reasonable for community contributions, or does it filter the long tail before it reaches a PR?**

Picking a default unilaterally would lock in the wrong choice if your users actually behave differently than we'd guess. No timeline.

## References

- [build123d#1270](https://github.com/gumyr/build123d/pull/1270) — the integration that brings the question into focus
- [3.10.0 schema-foundation milestone](https://github.com/MorePET/mat/releases/tag/v3.10.0) — `_sources` provenance + licensing gate
- [`docs/data-policy.md`](https://github.com/MorePET/mat/blob/main/docs/data-policy.md) — the bar for shipped data
- [#42](https://github.com/MorePET/mat/issues/42) — sibling discussion on JS/TS package for the same data

---

# [Comment #1]() by [bernhard-42]()

_Posted on May 7, 2026 at 05:03 PM_

ad 1.
I have no idea. I guess we need to publish the material system for build123d and learn as we walk.

ad 2.

I am not sure the schema is the biggest hurdle. I find the py-materials and mat-vis API surprisingly hard to use.
But, I am not an engineer or material expert, just a user that wants physical and visual properties of materials.

**Creating vs using materials**

The whole Readme seems to focus on creating materials, but aren't there existing materials?

It starts with the Readme:
- "Quick Start -> Creating Materials": But wait, I thought pymat comes with materials? I want to use materials and not immediately create them.
- When I get to "Chainable Material Hierarchy", I read about hierarchies before I understand the basics (how to access materials, what is a material, what properties are supported, what are grades, what are hierarchies, ...) And then I get told how to create a material that is already defined in the package. Not clear why?
- When I get down to "Direct Material Access" I need to realize that this is about accessing pymat materials, but it doesn't talk about: listing all available materials, showing existing properties of integrated materials, how to use them, ... All of that I would have expected in "Quick Start"
- The `finish`/ `finishes` approach is hardly documented

**Some unusual or complicated Python patterns (at least for me)**

When I want to understand the package and use it, I faced a few surprises

- `module[name]` as in `pymat["stainless"]` - mypy flagged it as an error
- Why do normal methods end with `_` (`grade_`, ...). I think it is against PEP8 (you only use it to avoid conflicts with Python keywords)
- Due to all the indirection and properties it is pretty hard to debug for a new user (try debugging `Vis.to_threejs()`)

**Why do I mention this?**

"A user who just wants density for shape.mass (your Level-2 ergonomic)" might already struggle with using the library. The difference between using a material (`from pymat import stainless`) and creating materials is unclear. 
So the answer is yes, both Readme and API need to be much easier to digest.

**Contributions**

Before creating content for a new package/system I first want to use and understand it with existing content (here materials), feel the value and experience the gaps. If I like the package, I am willing to contribute to fill the gaps.
And only then I face the toml schema. 

- Adding a material (TOML) Should be easy. Copy e.g. data/metals.toml, edits values. No code, no patterns, no tests required. 
- And regarding code PRs, given the scope of pymat (a hierachical material DB) I find py-materials already a bit overwhelming.


