# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-08

### BREAKING CHANGES
- Material constructor now accepts property groups as keyword arguments (mechanical={}, thermal={}, optical={}, pbr={}, etc.)
- Clearer separation: **Optical properties** (physics/measured) are now separate from **PBR properties** (visualization/rendering)
- `density` and `color` remain as convenience parameters for backward compatibility
- Manual `__init__` approach replaced with `@dataclass` + comprehensive `__post_init__` handling

### Added
- Property group kwargs in Material constructor for all property domains
- Auto-generated README from integration tests (doc-as-tested-code paradigm)
- Comprehensive test suite `test_readme_examples.py` with 40+ examples
- README generator script (`scripts/generate_readme.py`)
- README template with clear documentation (`docs/README_TEMPLATE.md`)
- Improved docstrings clarifying optical (physics) vs PBR (visualization) distinction
- Full documentation of constructor usage patterns

### Changed
- Material constructor is now more flexible and discoverable
- All property groups can be set during initialization
- Better separation of concerns between physics and visualization properties
- Improved error handling in `apply_to()` method (already in v0.1.2)

### Documentation
- Comprehensive README generated from tested examples
- Clear examples for all major features
- Property group usage patterns documented
- Material category overview

## [0.1.2] - 2025-01-08

### Added
- Comprehensive error handling in `Material.apply_to()` method
- Support for applying materials to any object (not just build123d Shapes)
- New test suite `test_apply_to.py` with error handling tests
- Graceful fallback for non-Shape objects (only sets `.material` attribute)

### Changed
- `apply_to()` now works with custom objects, setting only the `.material` attribute
- Better error messages for immutable objects with helpful messages
- Type hints updated to use `TypeVar` for generic object support

### Fixed
- No longer crashes when applying material to objects without `volume` or `color` attributes
- Proper TypeError raised for immutable objects with helpful messages

## [0.1.1] - 2025-01-08

### Added
- **Gases category** with common gases and cryogenic liquids
- Air, Nitrogen (N2), Oxygen (O2), Argon, CO2, Helium, Hydrogen, Neon, Xenon, Methane
- Cryogenic variants: Liquid Nitrogen, Liquid Helium, Dry Ice
- Vacuum material (for reference)
- Properties at STP (20°C, 1 atm) by default
- Use `factories.air(temp, pressure)` for temperature/pressure-dependent properties

### Changed
- Updated README with gases category
- Added gases to material registry

## [0.1.0] - 2025-01-08

### Added
- Initial release of hierarchical material library
- **Core Features**:
  - Chainable material hierarchy (grades, tempers, treatments, vendors)
  - Property inheritance through hierarchy
  - Lazy loading of material categories
  - TOML-based material definitions
  - build123d integration with `apply_to()` and automatic mass calculation
  - PBR rendering properties for visualization

- **Material Categories**:
  - **Metals**: Stainless steel (304, 316L, 17-4 PH), Aluminum (6061, 7075, 2024), Copper (OFHC), Tungsten, Lead, Titanium, Brass
  - **Scintillators**: LYSO, BGO, NaI, CsI, LaBr3, PWO, Plastic scintillators
  - **Plastics**: PEEK, Delrin, Ultem, PTFE, ESR, Nylon, PLA, ABS, PETG, TPU, Vespel, Torlon, PCTFE, PMMA, PE, PC
  - **Ceramics**: Alumina, Macor, Zirconia, Glass, Beryllia, Yttria
  - **Electronics**: FR4, Rogers, Kapton, Copper PCB, Solder, Ferrite, Epoxy
  - **Liquids**: Water, Heavy Water, Mineral Oil, Glycerol, Silicone Oil

- **Property Groups**:
  - Mechanical, Thermal, Electrical, Optical, PBR, Manufacturing, Compliance, Sourcing

- **Advanced Features**:
  - `periodictable` integration for formula-based property enrichment
  - Factory functions for temperature-dependent materials (water, air, saline)
  - Direct material access via registry
  - Full pytest test suite

---

## Release Notes

### Version Numbering
This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new features (backward compatible)
- **PATCH** version for bug fixes (backward compatible)

### Installation
```bash
# Install latest release
uv add git+https://github.com/MorePET/py-mat.git@latest

# Install specific version
uv add git+https://github.com/MorePET/py-mat.git@v1.0.0
```

### Links
- **GitHub**: https://github.com/MorePET/py-mat
- **Issues**: https://github.com/MorePET/py-mat/issues

[1.0.0]: https://github.com/MorePET/py-mat/compare/v0.1.2...v1.0.0
[0.1.2]: https://github.com/MorePET/py-mat/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/MorePET/py-mat/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/MorePET/py-mat/releases/tag/v0.1.0

### Added
- Comprehensive error handling in `Material.apply_to()` method
- Support for applying materials to any object (not just build123d Shapes)
- New test suite `test_apply_to.py` with error handling tests
- Graceful fallback for non-Shape objects (only sets `.material` attribute)

### Changed
- `apply_to()` now works with custom objects, setting only the `.material` attribute
- Better error messages for immutable objects (int, str, tuple, None)
- Type hints updated to use `TypeVar` for generic object support

### Fixed
- No longer crashes when applying material to objects without `volume` or `color` attributes
- Proper TypeError raised for immutable objects with helpful messages

## [0.1.1] - 2025-01-08

### Added
- **Gases category** with common gases and cryogenic liquids:
  - Air, Nitrogen (N2), Oxygen (O2), Argon, CO2, Helium, Hydrogen, Neon, Xenon, Methane
  - Cryogenic variants: Liquid Nitrogen, Liquid Helium, Dry Ice
  - Vacuum material (for reference)
- Properties at STP (20°C, 1 atm) by default
- Use `factories.air(temp, pressure)` for temperature/pressure-dependent properties

### Changed
- Updated README with gases category
- Added gases to material registry

## [0.1.0] - 2025-01-08

### Added
- Initial release of hierarchical material library
- **Core Features**:
  - Chainable material hierarchy (grades, tempers, treatments, vendors)
  - Property inheritance through hierarchy
  - Lazy loading of material categories
  - TOML-based material definitions
  - build123d integration with `apply_to()` and automatic mass calculation
  - PBR rendering properties for visualization
  
- **Material Categories**:
  - **Metals**: Stainless steel (304, 316L, 17-4 PH), Aluminum (6061, 7075, 2024), Copper (OFHC), Tungsten, Lead, Titanium, Brass
  - **Scintillators**: LYSO (Ce-doped, vendor variants), BGO, NaI(Tl), CsI (Tl, Na), LaBr3, PWO, Plastic scintillators
  - **Plastics**: PEEK, Delrin, Ultem, PTFE, ESR (3M Vikuiti), Nylon, PLA, ABS, PETG, TPU, Vespel, Torlon, PCTFE, PMMA, PE (HDPE, LDPE, UHMWPE), PC
  - **Ceramics**: Alumina (99.5%, 99.9%), Macor, Zirconia, Glass (borosilicate, fused silica, BK7), Beryllia, Yttria
  - **Electronics**: FR4, Rogers (4350B), Kapton, Copper PCB (1oz, 2oz, gold-plated), Solder (Sn63Pb37, SAC305), Ferrite, Epoxy potting
  - **Liquids**: Water (20°C default), Heavy Water (D2O), Mineral Oil, Glycerol, Silicone Oil, Ice
  
- **Property Groups**:
  - Mechanical: density, Young's modulus, yield strength, hardness, etc.
  - Thermal: melting point, thermal conductivity, expansion coefficient
  - Electrical: resistivity, conductivity, dielectric constant
  - Optical: refractive index, transparency, light yield (scintillators)
  - PBR: base color, metallic, roughness (for visualization)
  - Manufacturing: machinability, printability, weldability
  - Compliance: RoHS, REACH, food-safe, biocompatible
  - Sourcing: cost, availability, suppliers

- **Advanced Features**:
  - `periodictable` integration for formula-based property enrichment
  - Factory functions for temperature-dependent materials:
    - `water(temperature_c)` - water at specific temperature (0-100°C)
    - `air(temperature_c, pressure_atm)` - air at specific conditions
    - `saline(concentration_pct, temperature_c)` - saline solutions
  - Direct material access via registry
  - Full pytest test suite

- **Documentation**:
  - Comprehensive README with usage examples
  - Release process documentation with `latest` tag pattern
  - MIT License

### Technical Details
- Built with `hatchling` for easy installation
- Compatible with `uv` package manager
- Requires Python >= 3.11
- Optional dependencies: `periodictable`, `pymatgen`, `build123d`

---

## Release Notes

### Version Numbering
This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new features (backward compatible)
- **PATCH** version for bug fixes (backward compatible)

### Installation
```bash
# Install latest release
uv add git+https://github.com/MorePET/py-mat.git@latest

# Install specific version
uv add git+https://github.com/MorePET/py-mat.git@v0.1.2
```

### Links
- **GitHub**: https://github.com/MorePET/py-mat
- **Issues**: https://github.com/MorePET/py-mat/issues

[0.1.2]: https://github.com/MorePET/py-mat/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/MorePET/py-mat/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/MorePET/py-mat/releases/tag/v0.1.0

