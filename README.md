# pymat

A hierarchical material library for CAD applications with build123d integration.

## Features

- **Hierarchical Materials**: Chain grades, tempers, treatments, and vendors
- **Property Inheritance**: Children inherit parent properties unless overridden
- **Lazy Loading**: Categories load on first access
- **TOML Data Storage**: Easy-to-edit material definitions
- **build123d Integration**: Apply materials to shapes with automatic mass calculation
- **PBR Rendering**: Physically-based rendering properties for visualization
- **periodictable Integration**: Auto-fill density from chemical formulas

## Installation

```bash
# Basic installation
pip install pymat

# With periodictable support
pip install pymat[periodictable]

# With build123d support
pip install pymat[build123d]

# Full installation
pip install pymat[all]
```

Or using uv:

```bash
uv add pymat
uv add pymat[all]
```

## Quick Start

```python
from pymat import stainless, aluminum, lyso

# Chainable hierarchy
housing = stainless.s316L.electropolished.apply_to(Box(50, 50, 10))

# Direct access
crystal = lyso.apply_to(Box(10, 10, 30))
bracket = aluminum.a6061.T6.apply_to(Box(30, 20, 5))

# Check properties
print(housing.material.properties.pbr.roughness)
print(crystal.material.properties.optical.light_yield)
print(bracket.mass)  # Automatically calculated from density
```

## Material Categories

- **Metals**: Stainless steel, aluminum, copper, tungsten, lead, titanium, brass
- **Scintillators**: LYSO, BGO, NaI, CsI, LaBr3, PWO, plastic scintillators
- **Plastics**: PEEK, Delrin, Ultem, PTFE, ESR, Nylon, PLA, ABS, PETG, TPU, PMMA, PE, PC
- **Ceramics**: Alumina, Macor, Zirconia, Glass (borosilicate, fused silica, BK7)
- **Electronics**: FR4, Rogers, Kapton, copper PCB, solder, ferrite
- **Liquids**: Water, Heavy Water, Mineral Oil, Glycerol, Silicone Oil
- **Gases**: Air, Nitrogen, Oxygen, Argon, CO₂, Helium, Hydrogen, Neon, Xenon, Methane, Vacuum

## Property Groups

Each material can have properties in these domains:

- **Mechanical**: density, Young's modulus, yield strength, hardness
- **Thermal**: melting point, thermal conductivity, expansion coefficient
- **Electrical**: resistivity, conductivity, dielectric constant
- **Optical**: refractive index, light yield, decay time (scintillators)
- **PBR**: base color, metallic, roughness (for visualization)
- **Manufacturing**: machinability, printability, weldability
- **Compliance**: RoHS, REACH, food-safe, biocompatible

## Adding Custom Materials

Create a TOML file:

```toml
[my_alloy]
name = "My Custom Alloy"
formula = "Fe0.8Ni0.2"

[my_alloy.mechanical]
density = 8.1
yield_strength = 450

[my_alloy.pbr]
base_color = [0.7, 0.7, 0.75, 1.0]
metallic = 1.0
roughness = 0.4
```

Load it:

```python
from pymat import load_toml

materials = load_toml("my_materials.toml")
my_alloy = materials["my_alloy"]
```

## License

MIT

