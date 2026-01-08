"""
Property dataclasses for materials.

Organized by physical/engineering domain:
- MechanicalProperties: structural and deformation behavior
- ThermalProperties: temperature-related properties
- ElectricalProperties: electrical conductivity and dielectric behavior
- OpticalProperties: light interaction and scintillator-specific properties
- PBRProperties: physically-based rendering for visualization
- ManufacturingProperties: machinability, printability, weldability
- ComplianceProperties: regulatory and material suitability
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class MechanicalProperties:
    """Structural and deformation behavior."""
    density: Optional[float] = None              # g/cm³
    youngs_modulus: Optional[float] = None       # GPa
    shear_modulus: Optional[float] = None        # GPa
    poissons_ratio: Optional[float] = None       # dimensionless
    yield_strength: Optional[float] = None       # MPa
    tensile_strength: Optional[float] = None     # MPa
    compressive_strength: Optional[float] = None # MPa
    elongation: Optional[float] = None           # % at break
    hardness_vickers: Optional[float] = None     # HV (Vickers hardness)
    hardness_rockwell: Optional[float] = None    # HR (Rockwell hardness)
    fracture_toughness: Optional[float] = None   # MPa·m^0.5


@dataclass
class ThermalProperties:
    """Temperature-related properties."""
    melting_point: Optional[float] = None        # °C
    glass_transition: Optional[float] = None     # °C (for polymers)
    thermal_conductivity: Optional[float] = None # W/(m·K)
    specific_heat: Optional[float] = None        # J/(kg·K)
    thermal_expansion: Optional[float] = None    # µm/(m·K) or 1e-6/K
    max_service_temp: Optional[float] = None     # °C
    min_service_temp: Optional[float] = None     # °C
    thermal_shock_resistance: Optional[str] = None # "excellent", "good", "fair", "poor"


@dataclass
class ElectricalProperties:
    """Electrical conductivity and dielectric behavior."""
    resistivity: Optional[float] = None          # Ω·m
    conductivity: Optional[float] = None         # S/m
    dielectric_constant: Optional[float] = None  # relative permittivity (εr)
    dielectric_loss_tangent: Optional[float] = None # tan(δ)
    breakdown_voltage: Optional[float] = None    # kV/mm
    volume_resistivity: Optional[float] = None   # Ω·cm


@dataclass
class OpticalProperties:
    """
    Physical optical properties (measured values, physics calculations).
    
    These are PHYSICS properties, not visualization/rendering properties.
    For visualization, see PBRProperties.
    """
    # Basic optical properties
    refractive_index: Optional[float] = None     # n at 550nm (default)
    transparency: Optional[float] = None         # % transmission (0-100) - MEASURED VALUE
    absorption_coefficient: Optional[float] = None # 1/cm
    absorption_length: Optional[float] = None    # mm (inverse of coefficient)
    
    # Scintillator properties (detector physics)
    light_yield: Optional[float] = None          # photons/MeV
    decay_time: Optional[float] = None           # ns (mean decay time)
    rise_time: Optional[float] = None            # ns
    emission_peak: Optional[float] = None        # nm (peak emission wavelength)
    emission_range: Optional[tuple] = None       # (min_nm, max_nm)
    
    # Radiation interaction (detector/shielding physics)
    radiation_length: Optional[float] = None     # cm (X₀ for photons)
    interaction_length: Optional[float] = None   # cm (λ for hadrons)
    moliere_radius: Optional[float] = None       # cm
    energy_resolution: Optional[float] = None    # % at 1 MeV (for detectors)


@dataclass
class PBRProperties:
    """
    Physically-based rendering properties for visualization (NOT physics).
    
    These control how the material LOOKS in 3D viewers and renders.
    They may differ from physical optical properties intentionally.
    
    For physics/measured optical properties, see OpticalProperties.
    """
    # Surface appearance
    base_color: tuple = (0.8, 0.8, 0.8, 1.0)  # RGBA (0-1) - Alpha is VISUAL opacity
    metallic: float = 0.0                        # 0=dielectric, 1=metal
    roughness: float = 0.5                       # 0=glossy, 1=rough
    emissive: tuple = (0, 0, 0)                  # RGB emitted light
    
    # Transparency (RENDERING property, not physical measurement)
    ior: float = 1.5                             # index of refraction (for rendering)
    transmission: float = 0.0                    # 0=opaque, 1=transparent (volumetric)
    clearcoat: float = 0.0                       # secondary glossy layer
    
    # Texture maps (paths or URIs)
    normal_map: Optional[str] = None
    roughness_map: Optional[str] = None
    metallic_map: Optional[str] = None
    ambient_occlusion_map: Optional[str] = None


@dataclass
class ManufacturingProperties:
    """Machinability, weldability, printability."""
    # General manufacturability
    machinability: Optional[float] = None        # % relative to free-cutting steel (100%)
    weldability: Optional[str] = None            # "excellent", "good", "fair", "poor"
    formability: Optional[str] = None            # "excellent", "good", "fair", "poor"
    castability: Optional[str] = None            # "excellent", "good", "fair", "poor"
    
    # CNC machining
    cutting_speed: Optional[float] = None        # m/min (recommended)
    feed_rate: Optional[float] = None            # mm/rev
    tool_material: Optional[str] = None          # "HSS", "carbide", "ceramic", "diamond"
    
    # 3D printing
    printable_fdm: Optional[bool] = None         # FDM/FFF
    printable_sla: Optional[bool] = None         # SLA/DLP
    printable_sls: Optional[bool] = None         # SLS
    printable_binder_jet: Optional[bool] = None  # Binder jetting
    print_nozzle_temp: Optional[float] = None    # °C (FDM)
    print_bed_temp: Optional[float] = None       # °C (FDM)
    print_chamber_temp: Optional[float] = None   # °C (for high-temp)
    print_support_removal: Optional[str] = None  # "easy", "moderate", "difficult"
    
    # Other processes
    anodizable: Optional[bool] = None
    polishable: Optional[bool] = None
    solderable: Optional[bool] = None


@dataclass
class ComplianceProperties:
    """Regulatory compliance and material suitability."""
    rohs_compliant: Optional[bool] = None
    reach_compliant: Optional[bool] = None
    halogen_free: Optional[bool] = None
    lead_free: Optional[bool] = None
    
    # Application suitability
    food_safe: Optional[bool] = None
    biocompatible: Optional[bool] = None
    uv_resistant: Optional[bool] = None
    radiation_resistant: Optional[bool] = None   # gamma, neutron, etc.
    flame_retardant: Optional[bool] = None
    
    # Recyclability
    recyclable: Optional[bool] = None
    recycling_symbol: Optional[int] = None       # 1-7 for plastics


@dataclass
class SourcingProperties:
    """Cost and availability information."""
    cost_per_kg: Optional[float] = None          # USD/kg (approximate, volatile)
    availability: Optional[str] = None           # "stock", "common", "specialty", "rare"
    lead_time_weeks: Optional[float] = None      # weeks
    suppliers: list = field(default_factory=list)  # list of supplier names


@dataclass
class AllProperties:
    """Container for all material properties."""
    mechanical: MechanicalProperties = field(default_factory=MechanicalProperties)
    thermal: ThermalProperties = field(default_factory=ThermalProperties)
    electrical: ElectricalProperties = field(default_factory=ElectricalProperties)
    optical: OpticalProperties = field(default_factory=OpticalProperties)
    pbr: PBRProperties = field(default_factory=PBRProperties)
    manufacturing: ManufacturingProperties = field(default_factory=ManufacturingProperties)
    compliance: ComplianceProperties = field(default_factory=ComplianceProperties)
    sourcing: SourcingProperties = field(default_factory=SourcingProperties)
    
    # Extra user properties
    custom: Dict[str, Any] = field(default_factory=dict)

