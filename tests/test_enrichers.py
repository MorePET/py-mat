"""
Test suite for material enrichment functionality.

Tests periodictable integration and external data sources.
"""

import pytest

from pymat import Material
from pymat.enrichers import enrich_all, enrich_from_periodictable


class TestPeriodictableEnrichment:
    """Test enrichment from periodictable library."""

    def test_enrich_simple_compound_extracts_composition(self):
        """
        Enriching a compound populates `composition` (element → atom
        count) and leaves `density` unset. Density for compounds cannot
        be derived from periodictable; use `enrich_from_matproj` for
        that. See ADR-0001.
        """
        mat = Material(name="Aluminum Oxide", formula="Al2O3")
        assert mat.density is None or mat.density == 0

        enrich_from_periodictable(mat)

        assert mat.composition == {"Al": 2, "O": 3}
        # Molar mass is always derivable from the formula via the
        # computed property — independent of enrichment.
        assert mat.molar_mass is not None
        assert abs(mat.molar_mass - 101.96) < 0.1  # Al2O3 = 2*26.98 + 3*16.00
        # Density is NOT set for compounds.
        assert mat.density is None or mat.density == 0

    def test_enrich_complex_compound_extracts_composition(self):
        """Same as above for a fractional-stoichiometry compound."""
        mat = Material(name="LYSO", formula="Lu1.8Y0.2SiO5")

        enrich_from_periodictable(mat)

        assert mat.composition == {"Lu": 1.8, "Y": 0.2, "Si": 1, "O": 5}
        assert mat.molar_mass is not None
        assert 440 < mat.molar_mass < 441  # Lu1.8Y0.2SiO5 ≈ 440.87
        assert mat.density is None or mat.density == 0

    def test_enrich_without_formula(self):
        """Test enrichment with no formula."""
        mat = Material(name="Test Material")

        # Should not crash
        result = enrich_from_periodictable(mat)

        assert result == mat

    @pytest.mark.skipif(
        not pytest.importorskip("periodictable", reason="periodictable not installed"),
        reason="periodictable not installed",
    )
    def test_composition_extraction(self):
        """Test that composition is extracted from formula."""
        mat = Material(name="Test", formula="H2O")

        enrich_from_periodictable(mat)

        # Should have extracted composition
        if mat.composition:
            assert "H" in mat.composition
            assert "O" in mat.composition

    def test_enrich_returns_material(self):
        """Test that enrichment returns the material."""
        mat = Material(name="Test", formula="Al2O3")

        try:
            result = enrich_from_periodictable(mat)
            assert result is mat
        except ImportError:
            pytest.skip("periodictable not installed")


class TestEnrichAll:
    """Test enrich_all function."""

    def test_enrich_all_with_periodictable_extracts_composition(self):
        """
        `enrich_all` with periodictable populates composition and
        leaves compound density unset — same contract as
        `enrich_from_periodictable` directly. See ADR-0001.
        """
        mat = Material(name="Test", formula="SiO2")

        result = enrich_all(mat, use_periodictable=True)

        assert result is mat
        assert mat.composition == {"Si": 1, "O": 2}
        assert mat.molar_mass is not None
        assert abs(mat.molar_mass - 60.09) < 0.1  # SiO2 = 28.09 + 2*16.00

    def test_enrich_all_without_periodictable(self):
        """Test enriching without periodictable."""
        mat = Material(name="Test")

        result = enrich_all(mat, use_periodictable=False)

        assert result is mat


class TestEnrichmentEdgeCases:
    """Test edge cases in enrichment."""

    @pytest.mark.skipif(
        not pytest.importorskip("periodictable", reason="periodictable not installed"),
        reason="periodictable not installed",
    )
    def test_enrich_invalid_formula(self):
        """Test enrichment with invalid formula."""
        mat = Material(name="Test", formula="XyZ123Invalid")

        # Should not crash, just skip enrichment
        enrich_from_periodictable(mat)

        # Density should remain None/0 (or what was there)
        assert True  # Just verify no exception

    @pytest.mark.skipif(
        not pytest.importorskip("periodictable", reason="periodictable not installed"),
        reason="periodictable not installed",
    )
    def test_enrich_already_has_density(self):
        """Test enriching material that already has density."""
        mat = Material(name="Test", formula="Al2O3", density=3.95)

        enrich_from_periodictable(mat)

        # Should keep existing density (not override)
        assert mat.density == 3.95


class TestCommonMaterialsEnrichment:
    """Test enrichment on common materials."""

    @pytest.mark.skipif(
        not pytest.importorskip("periodictable", reason="periodictable not installed"),
        reason="periodictable not installed",
    )
    def test_enrich_aluminum(self):
        """Test enriching aluminum."""
        mat = Material(name="Aluminum", formula="Al")

        enrich_from_periodictable(mat)

        assert mat.density is not None
        # Al density is ~2.7 g/cm³
        assert 2.5 < mat.density < 3.0

    @pytest.mark.skipif(
        not pytest.importorskip("periodictable", reason="periodictable not installed"),
        reason="periodictable not installed",
    )
    def test_enrich_copper(self):
        """Test enriching copper."""
        mat = Material(name="Copper", formula="Cu")

        enrich_from_periodictable(mat)

        assert mat.density is not None
        # Cu density is ~8.96 g/cm³
        assert 8.5 < mat.density < 9.5

    @pytest.mark.skipif(
        not pytest.importorskip("periodictable", reason="periodictable not installed"),
        reason="periodictable not installed",
    )
    def test_enrich_tungsten(self):
        """Test enriching tungsten."""
        mat = Material(name="Tungsten", formula="W")

        enrich_from_periodictable(mat)

        assert mat.density is not None
        # W density is ~19.3 g/cm³
        assert 18.5 < mat.density < 20.0
