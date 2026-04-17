"""mat-vis output format adapters — Three.js, glTF, MaterialX.

Converts generic scalars + texture bytes into renderer-specific formats.
Pure Python, zero dependencies (uses only stdlib xml.etree for MaterialX).

All functions take generic dicts — no Material class dependency:

    from adapters import to_threejs, to_gltf, export_mtlx
    result = to_threejs(scalars, textures)

Field name mapping follows docs/specs/field-name-mapping.md.
"""

from __future__ import annotations

import base64
import xml.etree.ElementTree as ET
from pathlib import Path

# ── Field name mapping tables ───────────────────────────────────
#
# mat-vis channel name -> renderer property name
# Canonical source: docs/specs/field-name-mapping.md

_THREEJS_TEX_MAP: dict[str, str] = {
    "color": "map",
    "normal": "normalMap",
    "roughness": "roughnessMap",
    "metalness": "metalnessMap",
    "ao": "aoMap",
    "displacement": "displacementMap",
    "emission": "emissiveMap",
}

_GLTF_TEX_MAP: dict[str, str] = {
    "color": "baseColorTexture",
    "normal": "normalTexture",
    "ao": "occlusionTexture",
    "emission": "emissiveTexture",
    # roughness + metalness are packed into metallicRoughnessTexture
    # handled separately in to_gltf()
}

_MTLX_TEX_MAP: dict[str, str] = {
    "color": "base_color",
    "normal": "normal",
    "roughness": "specular_roughness",
    "metalness": "metalness",
    "ao": "occlusion",
    "displacement": "displacement",
    "emission": "emission_color",
}


# ── Helpers ─────────────────────────────────────────────────────


def _to_data_uri(png_bytes: bytes) -> str:
    """Encode PNG bytes as a base64 data URI."""
    b64 = base64.b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _color_hex_to_int(hex_str: str) -> int:
    """Convert '#RRGGBB' hex string to an integer (Three.js color format).

    >>> _color_hex_to_int('#A0522D')
    10506797
    """
    return int(hex_str.lstrip("#"), 16)


def _color_hex_to_rgba(hex_str: str) -> list[float]:
    """Convert '#RRGGBB' to glTF [R, G, B, A] floats in [0, 1]."""
    h = hex_str.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return [r / 255.0, g / 255.0, b / 255.0, 1.0]


# ── Three.js adapter ───────────────────────────────────────────


def to_threejs(
    scalars: dict,
    textures: dict[str, bytes] | None = None,
) -> dict:
    """Convert to a Three.js MeshPhysicalMaterial parameter dict.

    Args:
        scalars: Material scalars. Expected keys (all optional):
            - metalness (float 0-1)
            - roughness (float 0-1)
            - color_hex (str '#RRGGBB')
            - ior (float)
            - transmission (float 0-1)
        textures: Channel name -> PNG bytes. Keys are mat-vis channel
            names: color, normal, roughness, metalness, ao,
            displacement, emission.

    Returns:
        Dict suitable for `new THREE.MeshPhysicalMaterial(result)`.
        Textures are embedded as base64 data URIs.
    """
    textures = textures or {}
    result: dict = {"type": "MeshPhysicalMaterial"}

    # Scalars
    if "metalness" in scalars and scalars["metalness"] is not None:
        result["metalness"] = scalars["metalness"]
    if "roughness" in scalars and scalars["roughness"] is not None:
        result["roughness"] = scalars["roughness"]
    if "color_hex" in scalars and scalars["color_hex"] is not None:
        result["color"] = _color_hex_to_int(scalars["color_hex"])
    if "ior" in scalars and scalars["ior"] is not None:
        result["ior"] = scalars["ior"]
    if "transmission" in scalars and scalars["transmission"] is not None:
        result["transmission"] = scalars["transmission"]

    # Textures as data URIs
    for channel, prop in _THREEJS_TEX_MAP.items():
        if channel in textures:
            result[prop] = _to_data_uri(textures[channel])

    return result


# ── glTF adapter ────────────────────────────────────────────────


def to_gltf(
    scalars: dict,
    textures: dict[str, bytes] | None = None,
) -> dict:
    """Convert to a glTF pbrMetallicRoughness material dict.

    Args:
        scalars: Same as to_threejs().
        textures: Same as to_threejs().

    Returns:
        Dict conforming to glTF 2.0 material schema. Textures are
        embedded as base64 data URIs in the 'uri' field. Does NOT
        pack metalness+roughness into a single texture (that requires
        image compositing which needs PIL or similar). Instead, scalar
        factors are used when separate maps are provided.

    Note:
        Full glTF compliance for metallicRoughnessTexture packing
        requires image processing (PIL/Pillow). This adapter provides
        a best-effort output using scalar factors and separate texture
        references. For production glTF export, consider using a
        library like pygltflib.
    """
    textures = textures or {}
    pbr: dict = {}
    material: dict = {"pbrMetallicRoughness": pbr}

    # Scalar factors
    if "metalness" in scalars and scalars["metalness"] is not None:
        pbr["metallicFactor"] = scalars["metalness"]
    if "roughness" in scalars and scalars["roughness"] is not None:
        pbr["roughnessFactor"] = scalars["roughness"]
    if "color_hex" in scalars and scalars["color_hex"] is not None:
        pbr["baseColorFactor"] = _color_hex_to_rgba(scalars["color_hex"])

    # IOR extension
    if "ior" in scalars and scalars["ior"] is not None:
        material.setdefault("extensions", {})["KHR_materials_ior"] = {"ior": scalars["ior"]}

    # Transmission extension
    if "transmission" in scalars and scalars["transmission"] is not None:
        material.setdefault("extensions", {})["KHR_materials_transmission"] = {
            "transmissionFactor": scalars["transmission"]
        }

    # Textures
    def _tex_ref(png_bytes: bytes) -> dict:
        return {"source": {"uri": _to_data_uri(png_bytes)}}

    for channel, prop in _GLTF_TEX_MAP.items():
        if channel in textures:
            if prop in ("normalTexture", "occlusionTexture", "emissiveTexture"):
                material[prop] = _tex_ref(textures[channel])
            else:
                pbr[prop] = _tex_ref(textures[channel])

    # metallicRoughnessTexture: only if BOTH metalness and roughness
    # textures are available (proper packing needs image processing,
    # so we note this limitation)
    if "metalness" in textures and "roughness" in textures:
        pbr["_note_metallicRoughnessTexture"] = (
            "Separate metalness and roughness textures provided. "
            "Pack into a single metallicRoughnessTexture (B=metal, G=rough) "
            "for full glTF compliance."
        )

    return material


# ── MaterialX adapter ──────────────────────────────────────────


def export_mtlx(
    scalars: dict,
    textures: dict[str, bytes] | None = None,
    output_dir: str | Path = ".",
    *,
    material_name: str = "Material",
) -> Path:
    """Export as MaterialX .mtlx XML with referenced PNG files.

    Args:
        scalars: Same as to_threejs().
        textures: Same as to_threejs(). PNGs are written to output_dir.
        output_dir: Directory for .mtlx and .png files.
        material_name: Name for the material in the .mtlx document.

    Returns:
        Path to the written .mtlx file.
    """
    textures = textures or {}
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Root element
    root = ET.Element("materialx", version="1.38")

    # Standard surface node
    sr = ET.SubElement(root, "standard_surface", name=f"SR_{material_name}", type="surfaceshader")

    # Scalar inputs
    if "metalness" in scalars and scalars["metalness"] is not None:
        ET.SubElement(sr, "input", name="metalness", type="float", value=str(scalars["metalness"]))
    if "roughness" in scalars and scalars["roughness"] is not None:
        ET.SubElement(
            sr, "input", name="specular_roughness", type="float", value=str(scalars["roughness"])
        )
    if "color_hex" in scalars and scalars["color_hex"] is not None:
        rgba = _color_hex_to_rgba(scalars["color_hex"])
        color_str = f"{rgba[0]:.4f}, {rgba[1]:.4f}, {rgba[2]:.4f}"
        ET.SubElement(sr, "input", name="base_color", type="color3", value=color_str)
    if "ior" in scalars and scalars["ior"] is not None:
        ET.SubElement(sr, "input", name="specular_IOR", type="float", value=str(scalars["ior"]))
    if "transmission" in scalars and scalars["transmission"] is not None:
        ET.SubElement(
            sr, "input", name="transmission", type="float", value=str(scalars["transmission"])
        )

    # Write texture PNGs and create image nodes
    for channel, png_bytes in textures.items():
        mtlx_input = _MTLX_TEX_MAP.get(channel)
        if mtlx_input is None:
            continue

        # Write PNG file
        png_filename = f"{material_name}_{channel}.png"
        png_path = out / png_filename
        png_path.write_bytes(png_bytes)

        # Image node
        img_node_name = f"IMG_{material_name}_{channel}"
        img = ET.SubElement(root, "tiledimage", name=img_node_name, type="color3")
        ET.SubElement(img, "input", name="file", type="filename", value=png_filename)

        # Connect texture to shader input
        ET.SubElement(sr, "input", name=mtlx_input, type="color3", nodename=img_node_name)

    # Surface material
    mat = ET.SubElement(root, "surfacematerial", name=material_name, type="material")
    ET.SubElement(
        mat, "input", name="surfaceshader", type="surfaceshader", nodename=f"SR_{material_name}"
    )

    # Write .mtlx file
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    mtlx_path = out / f"{material_name}.mtlx"
    tree.write(mtlx_path, encoding="unicode", xml_declaration=True)

    return mtlx_path
