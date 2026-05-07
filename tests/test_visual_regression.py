"""Visual regression tests — headless Three.js rendering via Playwright.

Proves the full pipeline:
    pymat.Material → .vis → to_threejs → build123d export_gltf → Three.js render → screenshot

Uses a self-contained HTML viewer (tests/visual_render.html) that loads
Three.js from CDN + our exported glTF. No ocp_vscode needed.

Requirements:
    pip install playwright build123d
    python -m playwright install chromium

Skip with: MAT_VIS_SKIP_VISUAL=1 (default)
Run:   MAT_VIS_SKIP_VISUAL=0 pytest tests/test_visual_regression.py -v -s
"""

from __future__ import annotations

import http.server
import json
import os
import threading
from pathlib import Path

import pytest

SKIP_VISUAL = os.environ.get("MAT_VIS_SKIP_VISUAL", "1") == "1"
OUTPUT_DIR = Path(__file__).parent / "visual_output"
RENDER_HTML = Path(__file__).parent / "visual_render.html"


@pytest.fixture(scope="module")
def file_server():
    """Serve test files (HTML + glTF) on localhost."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(OUTPUT_DIR), **kwargs)

        def log_message(self, *args):
            pass  # silence

    # Copy render HTML to output dir
    import shutil

    shutil.copy(RENDER_HTML, OUTPUT_DIR / "index.html")

    port = 8765
    server = http.server.HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


@pytest.fixture(scope="module")
def browser():
    """Launch headless Chromium."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("playwright not installed")

    pw = sync_playwright().start()
    b = pw.chromium.launch(headless=True, args=["--use-gl=swiftshader"])
    yield b
    b.close()
    pw.stop()


def _render_and_screenshot(browser, server_url: str, glb_path: Path, name: str) -> Path:
    """Load a glTF in the Three.js viewer, wait for render, extract canvas."""
    import base64

    out = OUTPUT_DIR / f"{name}.png"

    page = browser.new_page(viewport={"width": 800, "height": 600})
    page.goto(f"{server_url}/index.html?gltf={glb_path.name}")

    # Wait for Three.js to signal render complete
    page.wait_for_function("window.__renderComplete === true", timeout=15000)
    page.wait_for_timeout(500)

    # Extract canvas content directly (more reliable than page screenshot)
    data_url = page.evaluate('document.querySelector("canvas").toDataURL("image/png")')
    png_bytes = base64.b64decode(data_url.split(",")[1])
    out.write_bytes(png_bytes)

    page.close()
    return out


@pytest.mark.skipif(SKIP_VISUAL, reason="MAT_VIS_SKIP_VISUAL=1 (default)")
class TestHeadlessRender:
    """Full pipeline: Material → glTF → Three.js headless → screenshot."""

    def test_steel_cube(self, file_server, browser):
        """Metallic steel cube with PBR scalars."""
        from build123d import Box, export_gltf

        from pymat import Material

        shape = Box(10, 10, 10)
        m = Material(name="Steel")
        m.vis.metallic = 1.0
        m.vis.roughness = 0.3
        m.vis.base_color = (0.8, 0.8, 0.8, 1.0)
        shape.material = m

        glb = OUTPUT_DIR / "steel_cube.glb"
        export_gltf(shape, str(glb))
        assert glb.exists()

        screenshot = _render_and_screenshot(browser, file_server, glb, "steel_cube")
        assert screenshot.exists()
        size = screenshot.stat().st_size
        assert size > 5000, f"Screenshot too small ({size} bytes) — likely blank"
        print(f"steel_cube: {size} bytes")

        from tests._visual_compare import assert_matches_baseline

        assert_matches_baseline(screenshot, "steel_cube")

    def test_red_sphere(self, file_server, browser):
        """Red dielectric sphere."""
        from build123d import Sphere, export_gltf

        from pymat import Material

        shape = Sphere(8)
        m = Material(name="Red Plastic")
        m.vis.metallic = 0.0
        m.vis.roughness = 0.5
        m.vis.base_color = (0.8, 0.1, 0.1, 1.0)
        shape.material = m

        glb = OUTPUT_DIR / "red_sphere.glb"
        export_gltf(shape, str(glb))

        screenshot = _render_and_screenshot(browser, file_server, glb, "red_sphere")
        assert screenshot.exists()
        size = screenshot.stat().st_size
        assert size > 5000, f"Screenshot too small ({size} bytes)"
        print(f"red_sphere: {size} bytes")

        from tests._visual_compare import assert_matches_baseline

        assert_matches_baseline(screenshot, "red_sphere")

    def test_gold_cylinder(self, file_server, browser):
        """Gold metallic cylinder."""
        from build123d import Cylinder, export_gltf

        from pymat import Material

        shape = Cylinder(5, 15)
        m = Material(name="Gold")
        m.vis.metallic = 1.0
        m.vis.roughness = 0.2
        m.vis.base_color = (1.0, 0.84, 0.0, 1.0)
        shape.material = m

        glb = OUTPUT_DIR / "gold_cylinder.glb"
        export_gltf(shape, str(glb))

        screenshot = _render_and_screenshot(browser, file_server, glb, "gold_cylinder")
        assert screenshot.exists()
        size = screenshot.stat().st_size
        assert size > 5000
        print(f"gold_cylinder: {size} bytes")

        from tests._visual_compare import assert_matches_baseline

        assert_matches_baseline(screenshot, "gold_cylinder")

    def test_glass_transmission(self, file_server, browser):
        """Transparent glass sphere."""
        from build123d import Sphere, export_gltf

        from pymat import Material

        shape = Sphere(10)
        m = Material(name="Glass")
        m.vis.metallic = 0.0
        m.vis.roughness = 0.0
        m.vis.base_color = (0.95, 0.95, 1.0, 0.3)
        m.vis.ior = 1.52
        m.vis.transmission = 0.9
        shape.material = m

        glb = OUTPUT_DIR / "glass_sphere.glb"
        export_gltf(shape, str(glb))

        screenshot = _render_and_screenshot(browser, file_server, glb, "glass_sphere")
        assert screenshot.exists()
        size = screenshot.stat().st_size
        assert size > 3000
        print(f"glass_sphere: {size} bytes")

    def test_multi_material_assembly(self, file_server, browser):
        """Assembly with different materials per part."""
        from build123d import Box, Compound, Cylinder, Pos, export_gltf

        from pymat import Material

        base = Box(20, 20, 3)
        m_base = Material(name="Wood Base")
        m_base.vis.metallic = 0.0
        m_base.vis.roughness = 0.7
        m_base.vis.base_color = (0.6, 0.4, 0.2, 1.0)
        base.material = m_base

        pin = Pos(0, 0, 10) * Cylinder(3, 14)
        m_pin = Material(name="Chrome Pin")
        m_pin.vis.metallic = 1.0
        m_pin.vis.roughness = 0.1
        m_pin.vis.base_color = (0.9, 0.9, 0.9, 1.0)
        pin.material = m_pin

        assembly = Compound(children=[base, pin])

        glb = OUTPUT_DIR / "assembly.glb"
        export_gltf(assembly, str(glb))

        screenshot = _render_and_screenshot(browser, file_server, glb, "assembly")
        assert screenshot.exists()
        size = screenshot.stat().st_size
        assert size > 5000
        print(f"assembly: {size} bytes")


@pytest.mark.skipif(SKIP_VISUAL, reason="MAT_VIS_SKIP_VISUAL=1 (default)")
class TestAdapterOutput:
    """Verify adapter dict output (no rendering needed)."""

    def test_to_threejs_scalars(self):
        from pymat import Material
        from pymat.vis.adapters import to_threejs

        m = Material(name="Steel")
        m.vis.metallic = 1.0
        m.vis.roughness = 0.3
        m.vis.base_color = (0.8, 0.8, 0.8, 1.0)

        d = to_threejs(m)
        assert d["metalness"] == 1.0
        assert d["roughness"] == 0.3

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "steel_threejs.json").write_text(json.dumps(d, indent=2, default=str))

    def test_to_threejs_with_textures(self):
        from pymat import Material, vis
        from pymat.vis.adapters import to_threejs

        results = vis.search(category="metal", limit=1)
        if not results:
            pytest.skip("No metals in mat-vis")

        m = Material(name="Textured Metal")
        m.vis.metallic = 1.0
        m.vis.roughness = 0.3
        m.vis.source = results[0]["source"]
        m.vis.material_id = results[0]["id"]

        d = to_threejs(m)
        has_map = any(k in d for k in ("map", "normalMap", "roughnessMap", "metalnessMap"))

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        summary = {
            k: (v[:60] + "..." if isinstance(v, str) and len(v) > 60 else v) for k, v in d.items()
        }
        (OUTPUT_DIR / "metal_textured_threejs.json").write_text(
            json.dumps(summary, indent=2, default=str)
        )

        if has_map:
            assert d[next(k for k in ("map", "normalMap") if k in d)].startswith(
                "data:image/png;base64,"
            )


# ────────────────────────────────────────────────────────────────────
# Bernhard's mat-vis #285 multi-material grid
# https://github.com/MorePET/mat-vis/issues/285
# ────────────────────────────────────────────────────────────────────


# 25-material grid mirroring the repro Bernhard posted in mat-vis #285.
# Format: (label, source, material_id) — texture_scale and overrides
# from his code are not represented because they're per-instance render
# state on the build123d side, not Vis attributes (see py-mat #93 / the
# texture_scale discussion in build123d#1270).
#
# The grid is intentionally heterogeneous: textured materials (bricks,
# leather, wood, fabric, tiles, plates) test the texture-bytes
# pipeline; metallic + scalar-only entries (chrome, gold, glass, red
# wine, plastics) test the scalar-baking pipeline that #285 is about.
# A regression that flips multiple metals back to default-grey-plastic
# (the failure Bernhard documented) shows up immediately on the
# uploaded artifact.
BERNHARD_285_GRID: list[tuple[str, str, str]] = [
    # row 0 — paint, oxidized, chrome, glass
    ("car_red", "gpuopen", "Car Paint"),
    ("car_green", "gpuopen", "Car Paint"),
    ("bronze", "gpuopen", "Bronze Oxydized"),
    ("chrome", "gpuopen", "Chrome"),
    ("glass", "gpuopen", "Glass"),
    # row 1 — transparent / scalar-heavy / brushed metals
    ("red_wine", "gpuopen", "Red Wine"),
    ("gold", "gpuopen", "Gold"),
    ("carbon_coat", "gpuopen", "Carbon biColor Coat"),
    ("acryl", "physicallybased", "Plastic (Acrylic)"),
    ("steel", "gpuopen", "Stainless Steel Brushed"),
    # row 2 — flat alu, textured masonry/leather, patterned alu
    ("alu", "gpuopen", "Aluminum Brushed"),
    ("bricks", "gpuopen", "TH: Large Red Bricks"),
    ("leather", "gpuopen", "TH: Brown Fabric Leather"),
    ("alu_corr", "gpuopen", "Aluminum Corrugated"),
    ("alu_hexagon", "gpuopen", "Aluminum Hexagon"),
    # row 3 — perforated, wood, tiles, ambientcg metal
    ("perforated", "gpuopen", "Perforated Metal"),
    ("wood", "gpuopen", "Ivory Walnut Solid Wood"),
    ("tiles", "gpuopen", "Iberian Blue Ceramic Tiles"),
    ("tiles2", "gpuopen", "Tiles Black Long Variative"),
    ("brass_scratched", "ambientcg", "Metal 007"),
    # row 4 — fabric, ambientcg metal plates, gpuopen flooring, polyhaven
    ("carbon", "ambientcg", "Fabric 004"),
    ("plates", "ambientcg", "Metal Plates 006"),
    ("floor", "gpuopen", "Adelie Brown Luxury Flooring"),
    ("plank", "polyhaven", "Plank Flooring 03"),
    ("rock_wall", "polyhaven", "Rock Wall 16"),
]


@pytest.mark.skipif(SKIP_VISUAL, reason="MAT_VIS_SKIP_VISUAL=1 (default)")
class TestBernhardMatVis285Grid:
    """Renders Bernhard's exact 25-material grid from mat-vis #285's
    repro snippet, parametrized by tier. The artifact (PNG per tier)
    is the canonical visual checkpoint for **mat-vis #285** — every
    release-please PR's reviewer checklist requires inspecting these
    against the threejs-materials reference (Image 2 in the upstream
    issue).

    The visual failure mode #285 documents: most metals render as
    flat default-grey plastic because the gpuopen baker emits
    ``metalness=0.0``, ``roughness=0.5``, ``color=0xCCCCCC``,
    ``ior=1.5``, ``transmission=0.0`` for materials whose authored
    .mtlx scalars never made it into the rowmap. Textured paths still
    work (image bytes are forwarded); scalar paths regress.

    Strict ``xfail`` until upstream fix (PR mat-vis#294 merged but
    pending re-bake + ``mat-vis-client`` 0.7.0 release). When that
    ships and py-mat picks it up via ``>=mat-vis-client``, this test
    flips to passing — the strict marker prompts dropping the xfail.

    Per-material behavior: any single material that 404s (cache miss,
    name drift) is logged but does not fail the test — the artifact
    is still useful with N-1 materials. Total fetch failure (network
    outage) is skipped via the standard mat-vis 5xx-on-skip pattern.
    """

    GRID_COLS = 5
    GRID_SPACING = 30.0  # mm — matches Bernhard's `Pos(i*30, j*30, 0)` layout

    @pytest.mark.parametrize("tier", ["1k", "512", "256"])
    @pytest.mark.xfail(
        reason=(
            "mat-vis #285: gpuopen baker drops authored .mtlx scalars; "
            "most metals render as flat grey plastic. Upstream baker fix "
            "merged in mat-vis#294 (2026-05-06) — pending re-bake + "
            "mat-vis-client 0.7.0 release. Flips green when py-mat picks "
            "up the new dep version. Visual artifact for the failure "
            "mode: tests/visual_output/bernhard_285_grid_{tier}.png."
        ),
        strict=True,
    )
    def test_bernhard_grid_at_tier(self, file_server, browser, tier: str) -> None:
        from build123d import Compound, Pos, Sphere, export_gltf

        from pymat import Material
        from pymat.vis import Vis, to_threejs

        # Build the grid: Bernhard's `create_shader_ball` becomes a
        # plain Sphere here (the visual point is the *materials* on
        # them, not the geometry).
        spheres: list = []
        skipped: list[str] = []
        scalar_summary: list[dict] = []

        for idx, (label, source, material_id) in enumerate(BERNHARD_285_GRID):
            row = idx // self.GRID_COLS
            col = idx % self.GRID_COLS
            sb = Pos(col * self.GRID_SPACING, row * self.GRID_SPACING, 0) * Sphere(7)

            try:
                vis = Vis(source=source, material_id=material_id, tier=tier)
                m = Material(name=f"sb_{label}")
                m.vis.source = source
                m.vis.material_id = material_id
                m.vis.tier = tier
                # Snapshot the scalars before the export to detect the
                # default-grey regression up-front (cheaper than only
                # eyeballing the final PNG).
                scalar_summary.append({"label": label, "scalars": to_threejs(vis)})
                sb.material = m
                spheres.append(sb)
            except Exception as exc:
                # Don't bail — log + continue. A few 404s yield a still-
                # useful artifact; total failure is caught below.
                skipped.append(f"{label} ({source}/{material_id}) tier={tier}: {exc}")

        if not spheres:
            pytest.skip(
                "no materials in BERNHARD_285_GRID resolved at tier="
                f"{tier} (cache miss / network) — {len(skipped)} skipped"
            )

        # Compose + export
        scene = Compound(children=spheres)
        glb = OUTPUT_DIR / f"bernhard_285_grid_{tier}.glb"
        export_gltf(scene, str(glb))
        assert glb.exists()
        glb_size = glb.stat().st_size
        assert glb_size > 50_000, (
            f"glTF too small ({glb_size} bytes) at tier={tier} — "
            "textures probably did not inline"
        )

        # Render
        screenshot = _render_and_screenshot(
            browser, file_server, glb, f"bernhard_285_grid_{tier}"
        )
        assert screenshot.exists()
        png_size = screenshot.stat().st_size
        assert png_size > 5_000, (
            f"screenshot too small ({png_size} bytes) — likely blank"
        )

        # Persist scalar summary alongside the PNG so reviewers can
        # cross-reference what each ball reports for metalness /
        # roughness / color without poking the live substrate.
        (OUTPUT_DIR / f"bernhard_285_grid_{tier}.scalars.json").write_text(
            json.dumps(
                {"tier": tier, "rendered": len(spheres), "skipped": skipped, "items": scalar_summary},
                indent=2,
                default=str,
            )
        )

        # The actual #285 assertion: at least 5 of the rendered
        # materials must have NON-default scalars. The default-grey
        # fingerprint is metalness=0.0 + roughness=0.5 + color in
        # {0xCCCCCC, "#cccccc"}. If everything matches that, the
        # baker has regressed.
        DEFAULT_GREY_INTS = {0xCCCCCC}
        DEFAULT_GREY_HEX = {"#cccccc", "#CCCCCC"}
        non_default = 0
        for entry in scalar_summary:
            sc = entry["scalars"]
            if (
                sc.get("metalness") not in (0.0, None)
                or sc.get("roughness") not in (0.5, None)
                or (sc.get("color") not in DEFAULT_GREY_INTS and sc.get("color") not in DEFAULT_GREY_HEX)
            ):
                non_default += 1

        assert non_default >= 5, (
            f"only {non_default}/{len(scalar_summary)} materials at tier={tier} "
            "have non-default scalars — gpuopen baker regression. "
            f"See artifact: bernhard_285_grid_{tier}.png + .scalars.json. "
            f"Skipped (404 / cache): {len(skipped)}."
        )
