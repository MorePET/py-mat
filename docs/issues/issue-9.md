---
type: issue
state: closed
created: 2026-04-15T08:28:24Z
updated: 2026-04-15T10:52:14Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/MorePET/mat/issues/9
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-16T04:44:39.602Z
---

# [Issue 9]: [enrich_from_periodictable: no density computation for compounds](https://github.com/MorePET/mat/issues/9)

## Context

Three tests in \`tests/test_enrichers.py\` were silently broken for an unknown amount of time:

- \`TestPeriodictableEnrichment::test_enrich_simple_formula\` (\`Al2O3\`)
- \`TestPeriodictableEnrichment::test_enrich_complex_formula\` (\`Lu1.8Y0.2SiO5\`)
- \`TestEnrichAll::test_enrich_all_with_periodictable\` (\`SiO2\`)

They were hidden by the \`uv.lock\` mismatch (CI was failing at \`uv sync --frozen\` long before any test ran). Once CI was unblocked in #8, they surfaced and have been marked \`@pytest.mark.xfail(strict=True)\` as a placeholder so CI stays green while this is tracked here.

## Root cause

\`enrich_from_periodictable\` in \`src/pymat/enrichers.py\` does:

\`\`\`python
if not material.properties.mechanical.density and formula.density:
    material.properties.mechanical.density = formula.density
\`\`\`

\`periodictable.formula(...).density\` only returns a value for **pure elements**. For compounds it is always \`None\`:

\`\`\`
$ python -c "import periodictable as pt; print([(f, pt.formula(f).density) for f in ['Al2O3','SiO2','Lu1.8Y0.2SiO5','Fe','Au']])"
[('Al2O3', None), ('SiO2', None), ('Lu1.8Y0.2SiO5', None), ('Fe', 7.874), ('Au', 19.3)]
\`\`\`

So for any compound, the enricher silently does nothing on the density front. The tests assume the opposite.

## Proposed fix

Add a density-from-composition calculator to \`enrich_from_periodictable\`. Two plausible approaches:

1. **Mass-fraction weighted density** — iterate \`formula.atoms\`, weight each element's elemental density by its mass fraction. Rough but nonzero for most compounds.
2. **Look up a compound-density database** (not from periodictable). Materials Project / Matminer have compound densities; we already integrate Materials Project via \`enrich_from_matproj\`, so this would be a natural extension there, not in the periodictable path.

Option 1 is the honest fix for this function's current promise. Option 2 sidesteps periodictable entirely.

Whichever path: once done, remove the \`xfail\` markers from \`tests/test_enrichers.py\` lines 16–41, 57–69, and 86–105.

## Acceptance criteria

- [ ] \`enrich_from_periodictable(Material(formula="Al2O3"))\` sets a non-zero density
- [ ] \`enrich_from_periodictable(Material(formula="Lu1.8Y0.2SiO5"))\` sets density in the 6.5–7.5 g/cm³ range (matches LYSO target in existing test)
- [ ] \`enrich_all(..., use_periodictable=True)\` for \`SiO2\` sets a density
- [ ] \`xfail(strict=True)\` markers removed
- [ ] No regression in the other periodictable-dependent tests
---

# [Comment #1]() by [gerchowl]()

_Posted on April 15, 2026 at 10:52 AM_

Fixed in #14 (merged to dev: e2128911).

- `enrich_from_periodictable` docstring now explicitly says compound density is not derivable from periodictable (crystal packing required) and points at `enrich_from_matproj` for that path.
- Three latently-broken tests rewritten to check composition + computed molar mass (what actually works).
- `Material.molar_mass` + `molar_mass_qty` added as `@property` accessors parsing `self.formula` via new `pymat/elements.py` (mirror of `mat-rs/src/elements.rs`).
- See ADR-0001 (`docs/decisions/0001-derived-chemistry-properties-live-on-material.md`) for why this lives on `Material` rather than in a new `ChemicalProperties` group, and the upgrade trigger for revisiting that decision.

