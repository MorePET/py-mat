"""
End-to-end example: Material with physics + PBR, Three.js JSON output.

Demonstrates the `pymat.pbr` Protocol-based integration from ADR-0002.
Works with both the lite in-tree backend (no extra deps) and the rich
`threejs-materials` backend (install `pip install py-materials[pbr]`).

Run:
    python examples/pbr_integration.py

Outputs:
    - Physics properties to stdout
    - Three.js MeshPhysicalMaterial dict to stdout
    - Writes the JSON to `examples/output/steel_material.json` for
      downstream viewer consumption

To verify visually in ocp_vscode (manual, requires VS Code + the
OCP CAD Viewer extension):
    1. `pip install py-materials[pbr] build123d ocp-vscode`
    2. Run this script with `--visual` to render a shader_ball in the
       viewer (see the block at the bottom of this file)
    3. Take a screenshot from the viewer's camera panel for snapshot
       verification (automated headless snapshotting of ocp_vscode is
       not currently feasible — tracked as a follow-up)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pymat import Material
from pymat.pbr import PbrSource

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def build_steel_with_lite_pbr() -> Material:
    """
    Build a `Material` using only the native in-tree PBR backend.

    This path works with `pip install py-materials` — no extras
    needed. Physics users get a usable material with basic PBR
    scalar values; no texture maps.
    """
    return Material(
        name="Stainless Steel 304",
        density=8.0,
        formula="Fe",  # dominant element, approximated for molar mass
        mechanical={"youngs_modulus": 193, "yield_strength": 170},
        thermal={"melting_point": 1450, "thermal_conductivity": 15.1},
        pbr={
            "base_color": (0.75, 0.75, 0.77, 1.0),
            "metallic": 1.0,
            "roughness": 0.35,
        },
    )


def build_steel_with_rich_pbr() -> Material | None:
    """
    Build a `Material` using the rich `threejs-materials` backend.

    Requires `pip install py-materials[pbr]`. Downloads the
    "Stainless Steel Brushed" MaterialX material from
    matlib.gpuopen.com on first run and caches it for subsequent
    runs. Returns None if the extra is not installed.
    """
    try:
        from pymat.pbr import PbrProperties  # type: ignore[attr-defined]
    except ImportError:
        return None

    return Material(
        name="Brushed Stainless Steel",
        density=8.0,
        formula="Fe",
        mechanical={"youngs_modulus": 193, "yield_strength": 170},
        thermal={"melting_point": 1450, "thermal_conductivity": 15.1},
        pbr_source=PbrProperties.from_gpuopen("Stainless Steel Brushed"),
    )


def report(material: Material, label: str) -> dict:
    """Print a summary of a Material and return its Three.js dict."""
    print(f"\n=== {label} ===")
    print(f"  name:          {material.name}")
    print(f"  density:       {material.density} g/cm³")
    print(f"  formula:       {material.formula}")
    print(f"  molar mass:    {material.molar_mass} g/mol")
    print(f"  pbr_source set: {material.pbr_source is not None}")

    three_js = material.to_three_js_material_dict()
    print("  Three.js dict:")
    print(json.dumps(three_js, indent=4, sort_keys=True))

    # Sanity: whichever backend is active, it conforms to the Protocol.
    source: PbrSource = (
        material.pbr_source if material.pbr_source is not None else material.properties.pbr
    )
    assert isinstance(source, PbrSource), (
        f"Active PBR backend {type(source).__name__} does not conform to PbrSource"
    )
    return three_js


def main() -> int:
    lite_steel = build_steel_with_lite_pbr()
    lite_dict = report(lite_steel, "Lite backend (zero extra deps)")
    (OUTPUT_DIR / "steel_lite.json").write_text(
        json.dumps(lite_dict, indent=2, sort_keys=True) + "\n"
    )

    rich_steel = build_steel_with_rich_pbr()
    if rich_steel is not None:
        rich_dict = report(rich_steel, "Rich backend (threejs-materials)")
        (OUTPUT_DIR / "steel_rich.json").write_text(
            json.dumps(rich_dict, indent=2, sort_keys=True) + "\n"
        )
    else:
        print(
            "\n=== Rich backend skipped ===\n"
            "  Install `pip install py-materials[pbr]` to fetch MaterialX\n"
            "  materials from ambientcg / polyhaven / gpuopen / physicallybased.info."
        )

    print(f"\nJSON written to {OUTPUT_DIR.resolve()}")
    return 0


# ---------------------------------------------------------------------------
# Optional: ocp_vscode visual rendering block.
# ---------------------------------------------------------------------------
# This block is skipped by default. To run it interactively:
#
#     pip install py-materials[pbr] build123d ocp-vscode
#     python examples/pbr_integration.py --visual
#
# It requires VS Code with the OCP CAD Viewer extension running, and
# opens a `shader_ball` with the material applied. Manual screenshot
# capture is currently the only way to snapshot — automated headless
# snapshotting of ocp_vscode is tracked as a separate follow-up.


def visual_demo() -> int:  # pragma: no cover
    """Render a shader_ball with the rich steel material in ocp_vscode."""
    try:
        from build123d import Box
        from ocp_vscode import show  # type: ignore[import-not-found]
    except ImportError as e:
        print(f"Visual demo requires [pbr] + build123d + ocp_vscode: {e}")
        return 1

    # A build123d shader ball would be ideal but the helper lives in
    # `ocp_vscode.utils.create_shader_ball` and requires its own
    # tesselation; we use a simple Box to keep the example minimal.
    shape = Box(50, 50, 50)
    steel = build_steel_with_rich_pbr()
    assert steel is not None
    # Until build123d ships `Shape.material` as a first-class attribute
    # (tracked in issue #3 + pending build123d PR), we set it as an
    # ad-hoc attribute — matches the current ocp_vscode convention.
    shape.material = steel  # type: ignore[attr-defined]
    show(shape)
    return 0


if __name__ == "__main__":
    if "--visual" in sys.argv:
        sys.exit(visual_demo())
    sys.exit(main())
