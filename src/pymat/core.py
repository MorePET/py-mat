"""
Core Material class with hierarchy, chaining, and properties.

Supports:
- Hierarchical inheritance (parents -> children)
- Chainable syntax: stainless.s316L.electropolished.apply_to(part)
- Direct access: s316L.apply_to(part) (auto-registered if no collision)
- Property inheritance (children inherit parent properties unless overridden)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from build123d import Shape

from .properties import AllProperties, MechanicalProperties, OpticalProperties, PBRProperties

# Type variable for generic object application
T = TypeVar('T')


@dataclass
class Material:
    """
    A hierarchical, chainable material node.
    
    Properties cascade down the chain - children inherit from parents
    but can override any property at any level.
    
    Constructor parameters:
    - name: Material name (required)
    - density: Density in g/cm³ (convenience parameter)
    - color: Visualization color - RGB tuple (r, g, b) or RGBA (r, g, b, alpha)
    - formula: Chemical formula (e.g., "Al2O3")
    - composition: Element fractions dict
    - mechanical: Dict of mechanical properties (density, youngs_modulus, etc.)
    - thermal: Dict of thermal properties (melting_point, conductivity, etc.)
    - electrical: Dict of electrical properties (resistivity, dielectric_constant, etc.)
    - optical: Dict of optical properties (refractive_index, transparency, etc.) - PHYSICS
    - pbr: Dict of PBR visualization properties (base_color, metallic, roughness) - RENDERING
    - manufacturing: Dict of manufacturing properties (machinability, weldability, etc.)
    - compliance: Dict of compliance properties (rohs_compliant, food_safe, etc.)
    - sourcing: Dict of sourcing properties (cost_per_kg, availability, etc.)
    
    Example usage:
        Material(name="Steel", density=7.8, color=(0.7, 0.7, 0.7))
        Material(name="Steel", mechanical={"density": 7.8, "youngs_modulus": 200})
        Material(name="LYSO", optical={"transparency": 92, "refractive_index": 1.82})
    """
    
    # Identity
    name: str
    formula: Optional[str] = None                # Chemical formula (e.g., "Al2O3")
    composition: Optional[Dict[str, float]] = None  # element -> fraction
    
    # Convenience parameters (backward compatibility)
    density: Optional[float] = None              # g/cm³ (convenience for mechanical.density)
    color: Optional[tuple] = None                # RGB or RGBA for visualization
    
    # Hierarchy metadata
    grade: Optional[str] = None                  # e.g., "304", "6061"
    temper: Optional[str] = None                 # e.g., "T6", "annealed"
    treatment: Optional[str] = None              # e.g., "passivated", "anodized"
    vendor: Optional[str] = None                 # e.g., "saint_gobain", "hamamatsu"
    
    # Property groups as kwargs
    mechanical: Optional[Dict[str, Any]] = None
    thermal: Optional[Dict[str, Any]] = None
    electrical: Optional[Dict[str, Any]] = None
    optical: Optional[Dict[str, Any]] = None      # Physics properties, NOT visualization
    pbr: Optional[Dict[str, Any]] = None          # Visualization properties, NOT physics
    manufacturing: Optional[Dict[str, Any]] = None
    compliance: Optional[Dict[str, Any]] = None
    sourcing: Optional[Dict[str, Any]] = None
    
    # Properties (all domains)
    properties: AllProperties = field(default_factory=AllProperties)
    
    # Hierarchy (not shown in repr)
    parent: Optional[Material] = field(default=None, repr=False)
    _children: Dict[str, Material] = field(default_factory=dict, repr=False)
    _key: Optional[str] = field(default=None, repr=False)  # for registry
    
    def __post_init__(self):
        """Apply convenience parameters and property groups to properties object."""
        # Apply convenience params (backward compatibility)
        if self.density is not None:
            self.properties.mechanical.density = self.density
        
        if self.color is not None:
            if len(self.color) == 3:
                # RGB provided, add full opacity
                self.properties.pbr.base_color = (*self.color, 1.0)
            elif len(self.color) == 4:
                # RGBA provided
                self.properties.pbr.base_color = self.color
            else:
                raise ValueError(f"color must be RGB (3 values) or RGBA (4 values), got {len(self.color)}")
        
        # Apply property groups
        if self.mechanical:
            for key, value in self.mechanical.items():
                if hasattr(self.properties.mechanical, key):
                    setattr(self.properties.mechanical, key, value)
        
        if self.thermal:
            for key, value in self.thermal.items():
                if hasattr(self.properties.thermal, key):
                    setattr(self.properties.thermal, key, value)
        
        if self.electrical:
            for key, value in self.electrical.items():
                if hasattr(self.properties.electrical, key):
                    setattr(self.properties.electrical, key, value)
        
        if self.optical:
            for key, value in self.optical.items():
                if hasattr(self.properties.optical, key):
                    setattr(self.properties.optical, key, value)
        
        if self.pbr:
            for key, value in self.pbr.items():
                if hasattr(self.properties.pbr, key):
                    setattr(self.properties.pbr, key, value)
        
        if self.manufacturing:
            for key, value in self.manufacturing.items():
                if hasattr(self.properties.manufacturing, key):
                    setattr(self.properties.manufacturing, key, value)
        
        if self.compliance:
            for key, value in self.compliance.items():
                if hasattr(self.properties.compliance, key):
                    setattr(self.properties.compliance, key, value)
        
        if self.sourcing:
            for key, value in self.sourcing.items():
                if hasattr(self.properties.sourcing, key):
                    setattr(self.properties.sourcing, key, value)
    
    # =========================================================================
    # Chaining API
    # =========================================================================
    
    def __getattr__(self, name: str) -> Material:
        """
        Access child variants by attribute.
        
        Usage:
            stainless.s316L -> accesses s316L grade
            s316L.electropolished -> accesses treatment
        """
        if name.startswith("_"):
            raise AttributeError(name)
        if name in self._children:
            return self._children[name]
        
        available = list(self._children.keys())
        raise AttributeError(
            f"'{self.name}' has no variant '{name}'. "
            f"Available: {available if available else 'none'}"
        )
    
    def _add_child(self, key: str, **overrides) -> Material:
        """
        Internal: add a child node with inherited properties.
        
        Child inherits all properties from parent unless explicitly overridden.
        """
        # Inherit property objects (deep copy to avoid mutation)
        from copy import deepcopy
        inherited_props = deepcopy(self.properties)
        
        # Merge overridden properties
        override_props = overrides.pop("properties", {})
        if isinstance(override_props, dict):
            # Merge into existing properties (for simple properties)
            # For dataclass properties, individual fields override
            if "mechanical_overrides" in overrides:
                for k, v in overrides.pop("mechanical_overrides").items():
                    if v is not None:
                        setattr(inherited_props.mechanical, k, v)
            if "thermal_overrides" in overrides:
                for k, v in overrides.pop("thermal_overrides").items():
                    if v is not None:
                        setattr(inherited_props.thermal, k, v)
            if "electrical_overrides" in overrides:
                for k, v in overrides.pop("electrical_overrides").items():
                    if v is not None:
                        setattr(inherited_props.electrical, k, v)
            if "optical_overrides" in overrides:
                for k, v in overrides.pop("optical_overrides").items():
                    if v is not None:
                        setattr(inherited_props.optical, k, v)
            if "pbr_overrides" in overrides:
                for k, v in overrides.pop("pbr_overrides").items():
                    if v is not None:
                        setattr(inherited_props.pbr, k, v)
            if "manufacturing_overrides" in overrides:
                for k, v in overrides.pop("manufacturing_overrides").items():
                    if v is not None:
                        setattr(inherited_props.manufacturing, k, v)
        
        # Build child properties
        child_props = {
            "name": overrides.get("name", f"{self.name} {key}"),
            "formula": overrides.get("formula", self.formula),
            "composition": overrides.get("composition", self.composition),
            "properties": inherited_props,
            "parent": self,
            "_key": key,
        }
        
        # Carry forward metadata unless overridden
        for meta in ("grade", "temper", "treatment", "vendor"):
            child_props[meta] = overrides.get(meta, getattr(self, meta))
        
        # Remove used overrides
        for k in list(overrides.keys()):
            if k in ("name", "formula", "composition", "grade", "temper", "treatment", "vendor"):
                overrides.pop(k)
        
        # Store any remaining overrides in custom properties
        if overrides:
            child_props["properties"].custom.update(overrides)
        
        child = Material(**child_props)
        self._children[key] = child
        return child
    
    # =========================================================================
    # Chainable Methods
    # =========================================================================
    
    def grade_(self, key: str, **props) -> Material:
        """Add a grade variant (e.g., 304, 316L, 6061, a7075)."""
        return self._add_child(key, grade=key, **props)
    
    def temper_(self, key: str, **props) -> Material:
        """Add a temper/heat treatment (e.g., T6, O, annealed)."""
        return self._add_child(key, temper=key, **props)
    
    def treatment_(self, key: str, **props) -> Material:
        """Add a surface treatment (e.g., passivated, anodized, electropolished)."""
        return self._add_child(key, treatment=key, **props)
    
    def vendor_(self, key: str, **props) -> Material:
        """Add a vendor-specific variant."""
        return self._add_child(key, vendor=key, **props)
    
    def variant_(self, key: str, **props) -> Material:
        """Add a generic variant (dopant, alloy composition, etc.)."""
        return self._add_child(key, **props)
    
    # =========================================================================
    # Application to Shapes
    # =========================================================================
    
    def apply_to(self, obj):
        """
        Apply this material to an object.
        
        For build123d Shapes: sets material, color, and calculates mass
        For other objects: sets obj.material = self
        
        Args:
            obj: Object to apply material to (build123d Shape or any object)
            
        Returns:
            The modified object
            
        Raises:
            TypeError: If obj doesn't support attribute assignment
            
        Example:
            # build123d Shape - full features
            crystal = Box(10, 10, 10)
            lyso.apply_to(crystal)  # Sets: material, color, mass
            
            # Custom object - just material attribute
            class MyPart:
                pass
            part = MyPart()
            stainless.apply_to(part)  # Sets: part.material = stainless
        """
        # Check if object supports attribute assignment
        try:
            obj.material = self
        except (AttributeError, TypeError) as e:
            raise TypeError(
                f"Cannot apply material to {type(obj).__name__}: "
                f"object doesn't support attribute assignment ({e})"
            )
        
        # Try build123d-specific features (color, mass calculation)
        # Check for build123d Shape characteristics: has volume and color attributes
        try:
            if hasattr(obj, 'volume') and hasattr(obj, 'color'):
                # Set color from PBR
                color = self.properties.pbr.base_color
                if len(color) == 4:  # RGBA
                    # For build123d viewer: use RGB, transparency via alpha
                    obj.color = color[:3]
                    # Note: alpha would be set separately if shape supports it
                else:
                    obj.color = color
                
                # Calculate mass if density is available
                if self.properties.mechanical.density and self.properties.mechanical.density > 0:
                    # build123d volume is in mm³, density is g/cm³
                    # 1 cm³ = 1000 mm³, so g/mm³ = g/cm³ / 1000
                    density_g_mm3 = self.properties.mechanical.density / 1000
                    obj.mass = obj.volume * density_g_mm3
        
        except (AttributeError, TypeError):
            # If build123d-specific features fail, that's fine
            # The material attribute is already set, which is the minimum requirement
            pass
        
        return obj
    
    # =========================================================================
    # Information & Inspection
    # =========================================================================
    
    @property
    def path(self) -> str:
        """Full hierarchical path from root (e.g., 'aluminum.a7075.T6')."""
        parts = []
        node = self
        while node:
            part_key = node._key or node.name.lower().replace(" ", "_")
            parts.append(part_key)
            node = node.parent
        return ".".join(reversed(parts))
    
    @property
    def density(self) -> Optional[float]:
        """Density in g/cm³."""
        return self.properties.mechanical.density
    
    @density.setter
    def density(self, value: float) -> None:
        """Set density in g/cm³."""
        self.properties.mechanical.density = value
    
    @property
    def density_g_mm3(self) -> float:
        """Density in g/mm³ (for build123d calculations)."""
        if not self.density:
            return 0.0
        return self.density / 1000
    
    def mass_from_volume_mm3(self, volume_mm3: float) -> float:
        """Calculate mass in grams from volume in mm³."""
        return volume_mm3 * self.density_g_mm3
    
    def __repr__(self) -> str:
        """String representation showing path and density."""
        density_str = f"ρ={self.density} g/cm³" if self.density else "ρ=?"
        return f"Material({self.path!r}, {density_str})"
    
    def __str__(self) -> str:
        """Human-readable string."""
        return f"{self.name} ({self.path})"
    
    def info(self) -> str:
        """Detailed information about this material."""
        lines = [
            f"Material: {self.name}",
            f"Path: {self.path}",
            "",
            "Mechanical Properties:",
            f"  Density: {self.density} g/cm³" if self.density else "  Density: N/A",
            f"  Young's Modulus: {self.properties.mechanical.youngs_modulus} GPa" 
                if self.properties.mechanical.youngs_modulus else "",
            f"  Yield Strength: {self.properties.mechanical.yield_strength} MPa"
                if self.properties.mechanical.yield_strength else "",
        ]
        
        if self.formula:
            lines.append(f"Formula: {self.formula}")
        if self.composition:
            lines.append(f"Composition: {self.composition}")
        
        return "\n".join(line for line in lines if line)

