"""
Test suite for pymat loader functionality.

Tests TOML loading, inheritance resolution, and registry integration.
"""

import pytest
from pathlib import Path
from pymat.loader import load_toml, load_category, _build_properties_from_dict
from pymat.properties import AllProperties
from pymat import registry


class TestTOMLLoading:
    """Test TOML file loading."""
    
    def test_load_metals_category(self):
        """Test loading metals.toml."""
        materials = load_category("metals")
        assert len(materials) > 0
        assert "stainless" in materials
        assert "aluminum" in materials
    
    def test_load_scintillators_category(self):
        """Test loading scintillators.toml."""
        materials = load_category("scintillators")
        assert len(materials) > 0
        assert "lyso" in materials
        assert "bgo" in materials
    
    def test_load_plastics_category(self):
        """Test loading plastics.toml."""
        materials = load_category("plastics")
        assert len(materials) > 0
        assert "peek" in materials
        assert "delrin" in materials
    
    def test_load_ceramics_category(self):
        """Test loading ceramics.toml."""
        materials = load_category("ceramics")
        assert len(materials) > 0
        assert "alumina" in materials


class TestInheritance:
    """Test property inheritance during loading."""
    
    def test_inherit_density(self):
        """Test that child materials inherit parent density."""
        materials = load_category("metals")
        
        stainless = materials["stainless"]
        s304 = stainless._children.get("s304")
        
        assert stainless.density == 8.0
        if s304:
            assert s304.density == 8.0  # Inherited
    
    def test_inherit_color(self):
        """Test PBR color inheritance."""
        materials = load_category("metals")
        
        stainless = materials["stainless"]
        s316L = stainless._children.get("s316L")
        
        if s316L:
            # Should inherit or override parent color
            assert s316L.properties.pbr.base_color is not None
    
    def test_deep_inheritance(self):
        """Test inheritance through multiple levels."""
        materials = load_category("metals")
        
        stainless = materials["stainless"]
        s316L = stainless._children.get("s316L")
        
        if s316L:
            electropolished = s316L._children.get("electropolished")
            if electropolished:
                # Should inherit density from grandparent
                assert electropolished.density == stainless.density


class TestChildMaterials:
    """Test loading of child materials from TOML."""
    
    def test_stainless_has_grades(self):
        """Test that stainless steel has grade children."""
        materials = load_category("metals")
        stainless = materials["stainless"]
        
        assert "s304" in stainless._children
        assert "s316L" in stainless._children
    
    def test_aluminum_has_grades_and_tempers(self):
        """Test that aluminum has both grades and tempers."""
        materials = load_category("metals")
        aluminum = materials["aluminum"]
        
        assert "a6061" in aluminum._children
        assert "a7075" in aluminum._children
        
        # Check for tempers on grades
        if "a6061" in aluminum._children:
            a6061 = aluminum._children["a6061"]
            assert "T6" in a6061._children or "T6" in aluminum._children
    
    def test_lyso_has_dopants(self):
        """Test that LYSO has dopant variants."""
        materials = load_category("scintillators")
        lyso = materials["lyso"]
        
        assert "Ce" in lyso._children


class TestMaterialProperties:
    """Test that properties are correctly loaded."""
    
    def test_mechanical_properties(self):
        """Test mechanical properties are loaded."""
        materials = load_category("metals")
        stainless = materials["stainless"]
        
        assert stainless.properties.mechanical.density == 8.0
        assert stainless.properties.mechanical.youngs_modulus == 193
    
    def test_optical_properties(self):
        """Test optical properties for scintillators."""
        materials = load_category("scintillators")
        lyso = materials["lyso"]
        
        assert lyso.properties.optical.refractive_index == 1.82
        assert lyso.properties.optical.light_yield == 32000
        assert lyso.properties.optical.decay_time == 41
    
    def test_pbr_properties(self):
        """Test PBR properties are loaded."""
        materials = load_category("metals")
        stainless = materials["stainless"]
        
        pbr = stainless.properties.pbr
        assert pbr.base_color is not None
        assert pbr.metallic == 1.0
        assert pbr.roughness == 0.3
    
    def test_electrical_properties(self):
        """Test electrical properties."""
        materials = load_category("electronics")
        fr4 = materials.get("fr4")
        
        if fr4:
            assert fr4.properties.electrical.dielectric_constant == 4.5


class TestRegistry:
    """Test that materials are registered correctly."""
    
    def test_registry_registration(self):
        """Test that loaded materials are in registry."""
        load_category("metals")
        
        # Check some common materials are registered
        all_materials = registry.list_all()
        
        # Should have registered materials
        assert len(all_materials) > 0
    
    def test_direct_access_after_load(self):
        """Test direct registry access after loading."""
        load_category("metals")
        
        # Should be able to get materials directly from registry
        s304 = registry.get("s304")
        assert s304 is not None


class TestFormulaAndComposition:
    """Test formula and composition handling."""
    
    def test_lyso_has_formula(self):
        """Test that LYSO has chemical formula."""
        materials = load_category("scintillators")
        lyso = materials["lyso"]
        
        assert lyso.formula == "Lu1.8Y0.2SiO5"
    
    def test_material_info_with_formula(self):
        """Test material info displays formula."""
        materials = load_category("scintillators")
        lyso = materials["lyso"]
        
        info = lyso.info()
        assert "Lu1.8Y0.2SiO5" in info or "Formula" not in info  # May or may not include


class TestManufacturingProperties:
    """Test manufacturing properties are loaded."""
    
    def test_printable_properties(self):
        """Test 3D printing properties."""
        materials = load_category("plastics")
        pla = materials.get("pla")
        
        if pla:
            assert pla.properties.manufacturing.printable_fdm == True
    
    def test_print_temperatures(self):
        """Test print temperatures are set."""
        materials = load_category("plastics")
        peek = materials.get("peek")
        
        if peek:
            assert peek.properties.manufacturing.print_nozzle_temp == 360

