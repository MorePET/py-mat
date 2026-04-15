# 0001. Derived chemistry properties live on `Material`, not in a property group

- Status: Accepted
- Date: 2026-04-15
- Deciders: @gerchowl

## Context

`Material` has eight property groups today — `mechanical`, `thermal`,
`electrical`, `optical`, `pbr`, `manufacturing`, `compliance`, `sourcing`.
Each group is a dataclass of measured/authored values held on
`Material.properties`.

Chemistry-derived quantities don't fit cleanly into any of them. The first
concrete instance is **molar mass**: a scalar that is definitionally a
function of `composition` (element counts × atomic weights) and has no
experimental/authored value to store. The tests in `tests/test_enrichers.py`
previously assumed `enrich_from_periodictable` would populate a compound's
density from its formula, which is physically impossible without
crystallographic unit-cell data (ρ depends on atomic packing, not on the
weighted sum of elemental densities). See #9.

The primary consumer of this library — Monte Carlo particle transport (see
README, `mat-rs`) — needs molar mass constantly for mass↔atom fraction
conversions. They treat it as a one-liner property of the material, not as
a value to be looked up in a data table.

The Rust crate `rs-materials` already exposes molar mass as a computed
function of composition, with no stored field, via
`compute_molar_mass(&composition)` in `mat-rs/src/elements.rs`. The Python
API should match.

## Decision

**Derived chemistry properties live directly on `Material` as computed
`@property` accessors**, not inside a property group. They are not stored
in TOML data files and cannot be overridden by authors.

Concretely for this ADR: `Material.molar_mass` and `Material.molar_mass_qty`
(pint-wrapped) are `@property` methods that compute from
`Material.composition` using a local atomic-weights table in
`pymat/elements.py`.

## Consequences

**Enables**:

- Single source of truth — `formula` and `composition` are authoritative;
  derived quantities cannot drift from them.
- Parity with the Rust crate's API surface.
- Ergonomic access: `material.molar_mass` sits alongside `material.density`,
  `material.formula`, `material.composition` as top-level attributes — no
  `material.properties.chemical.molar_mass` indirection.
- No TOML data migration, no loader changes, no inheritance interactions
  (computed properties don't cascade from parent to child — they recompute
  per-material).

**Costs**:

- No authored override path for isotopically enriched materials (D₂O, ²³⁵U,
  etc.). These are real materials-science use cases but belong to a larger
  "isotope support" story the library doesn't yet tell. Tracked separately
  if/when needed.
- Derived-property accessors are not introspected by `Material.info()` or
  serialized in the same way as property-group fields.

**Rules out**:

- Storing molar mass as a stateful field (would invite drift).
- Putting molar mass inside `MechanicalProperties` (taxonomically wrong —
  mechanical is stress/strain/deformation; molar mass is chemistry).

## Alternatives considered

- **`MechanicalProperties.molar_mass`** — rejected: taxonomic mismatch and
  invites drift from `formula`.
- **New `ChemicalProperties` property group** — rejected *for now* as
  premature: a property group with one member is over-engineered. Reconsider
  under the upgrade trigger below.
- **Free function in `enrichers.py`**, e.g. `compute_molar_mass(material)` —
  rejected: poor ergonomics, breaks symmetry with `material.density` and
  `material.composition` which are already top-level.

## Upgrade trigger

Introduce a `ChemicalProperties` property group (and move `molar_mass` into
it) when **two or more** non-definitionally-derived chemistry properties
need a home. Candidates: heat of formation, oxidation state, standard
electrode potential, electronegativity, band gap, work function.

When that happens, `Material.molar_mass` remains as a shortcut `@property`
that reads from `properties.chemical.molar_mass` if set, falling back to
computation from `composition`. This preserves the API for existing
consumers.

Also revisit this ADR if isotope support lands — that introduces an override
use case (enriched fuels, D₂O) that needs authored storage.
