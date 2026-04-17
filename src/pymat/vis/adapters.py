"""
Output adapters — thin wrappers that map Material to mat-vis's
generic adapter functions.

The actual format logic (Three.js field names, glTF schema,
MaterialX XML) lives in _vendor_adapters.py (shipped by mat-vis).
These wrappers extract scalars + textures from a Material and
pass them through.

    from pymat.vis.adapters import to_threejs, to_gltf, export_mtlx
    result = to_threejs(material)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from pymat.vis._vendor_adapters import export_mtlx as _export_mtlx
from pymat.vis._vendor_adapters import to_gltf as _to_gltf
from pymat.vis._vendor_adapters import to_threejs as _to_threejs

if TYPE_CHECKING:
    from pymat.core import _MaterialInternal as Material


def _extract_scalars(material: Material) -> dict[str, Any]:
    """Extract PBR scalars from Material.properties.pbr as a plain dict."""
    pbr = material.properties.pbr
    # Map py-mat field names → mat-vis field names
    # See docs/specs/field-name-mapping.md: py-mat "metallic" → mat-vis "metalness"
    scalars: dict[str, Any] = {
        "metalness": pbr.metallic,
        "roughness": pbr.roughness,
        "base_color": pbr.base_color,
        "ior": pbr.ior,
        "transmission": pbr.transmission,
        "clearcoat": pbr.clearcoat,
        "emissive": pbr.emissive,
    }
    return scalars


def _extract_textures(material: Material) -> dict[str, bytes]:
    """Extract texture bytes from Material.vis.

    Only reads from .vis (the correct namespace for visual data).
    Legacy pbr.*_map fields are NOT merged here — those are handled
    by ocp_vscode's existing is_pymat path until deprecated.
    """
    if material.vis.source_id is None:
        return {}
    return material.vis.textures


def to_threejs(material: Material) -> dict[str, Any]:
    """Format as a Three.js MeshPhysicalMaterial-compatible dict.

    Reads PBR scalars from material.properties.pbr and texture maps
    from material.vis. Delegates to mat-vis's generic adapter.
    """
    return _to_threejs(_extract_scalars(material), _extract_textures(material))


def to_gltf(material: Material) -> dict[str, Any]:
    """Format as a glTF pbrMetallicRoughness material dict.

    Delegates to mat-vis's generic adapter. Note: glTF packing of
    metalness + roughness into one texture is handled by the
    mat-vis adapter.
    """
    result = _to_gltf(_extract_scalars(material), _extract_textures(material))
    result["name"] = material.name
    return result


def export_mtlx(material: Material, output_dir: Path) -> Path:
    """Export as a MaterialX .mtlx file + PNG textures on disk.

    Delegates to mat-vis's generic adapter.
    """
    safe_name = material.name.replace(" ", "_").replace("/", "_")
    return _export_mtlx(
        _extract_scalars(material),
        _extract_textures(material),
        output_dir,
        material_name=safe_name,
    )
