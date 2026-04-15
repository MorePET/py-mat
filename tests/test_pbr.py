"""
Tests for `pymat.pbr` — PbrSource Protocol + native backend serializer.

Covers the lite in-tree path (PBRProperties.to_three_js_dict) and the
Material.to_three_js_material_dict dispatch. The rich threejs-materials
backend is exercised via a duck-typed stub to avoid pulling the extra
into the base test dependency set. See ADR-0002.
"""

from __future__ import annotations

import pytest

from pymat import Material
from pymat.pbr import PbrSource
from pymat.properties import PBRProperties


class TestPbrSourceProtocol:
    """Native `PBRProperties` should satisfy the `PbrSource` Protocol."""

    def test_native_pbr_properties_is_pbr_source(self):
        pbr = PBRProperties()
        assert isinstance(pbr, PbrSource)

    def test_native_minimal_serialization(self):
        """Default PBRProperties emits only `color` (all other fields
        are at Three.js defaults and get omitted)."""
        pbr = PBRProperties()
        out = pbr.to_three_js_dict()
        assert out == {"color": [0.8, 0.8, 0.8]}

    def test_native_full_serialization(self):
        pbr = PBRProperties(
            base_color=(0.7, 0.2, 0.2, 0.8),
            metallic=1.0,
            roughness=0.25,
            transmission=0.3,
            clearcoat=0.5,
            normal_map="/path/to/normal.png",
        )
        out = pbr.to_three_js_dict()
        assert out["color"] == [0.7, 0.2, 0.2]
        assert out["metalness"] == 1.0
        assert out["roughness"] == 0.25
        assert out["transmission"] == 0.3
        assert out["clearcoat"] == 0.5
        assert out["opacity"] == pytest.approx(0.8)
        assert out["transparent"] is True
        assert out["normalMap"] == "/path/to/normal.png"


class TestMaterialToThreeJs:
    """`Material.to_three_js_material_dict()` picks the right backend."""

    def test_falls_back_to_native_pbr(self):
        steel = Material(
            name="Steel",
            density=7.85,
            pbr={"base_color": (0.6, 0.6, 0.65, 1.0), "metallic": 1.0},
        )
        out = steel.to_three_js_material_dict()
        assert out["color"] == [0.6, 0.6, 0.65]
        assert out["metalness"] == 1.0

    def test_pbr_source_takes_precedence(self):
        """When `pbr_source` is set, the native `properties.pbr` is ignored."""

        class FakeRichBackend:
            """Stub conforming to PbrSource Protocol."""

            def to_three_js_dict(self) -> dict:
                return {
                    "color": [0.91, 0.91, 0.88],
                    "metalness": 1.0,
                    "roughness": 0.05,
                    "normalMap": "textures/brushed_steel_normal.png",
                }

        steel = Material(
            name="Brushed Steel",
            density=7.85,
            pbr={"base_color": (0.3, 0.3, 0.3, 1.0)},  # would lose if used
            pbr_source=FakeRichBackend(),
        )
        out = steel.to_three_js_material_dict()
        # Rich backend's output, not the lite pbr dict.
        assert out["color"] == [0.91, 0.91, 0.88]
        assert out["normalMap"] == "textures/brushed_steel_normal.png"

    def test_pbr_source_stub_is_pbr_source(self):
        """Any class with `to_three_js_dict()` satisfies the Protocol."""

        class Stub:
            def to_three_js_dict(self):
                return {}

        assert isinstance(Stub(), PbrSource)

    def test_non_conforming_object_is_not_pbr_source(self):
        class NotPbr:
            pass

        assert not isinstance(NotPbr(), PbrSource)
