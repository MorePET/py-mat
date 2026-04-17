#!/usr/bin/env python3
"""Propose [vis] mappings for materials that don't have one.

Queries the mat-vis index via pymat.vis.search() and suggests
best-match appearances for each TOML-registered material.

Usage:
    # Preview proposed mappings
    python scripts/enrich_vis.py

    # Write proposed TOML patches to a file
    python scripts/enrich_vis.py --output proposed_vis.toml

    # Auto-apply top matches (use with care — review the PR)
    python scripts/enrich_vis.py --apply

Called by .github/workflows/enrich-vis.yml on each mat-vis release.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure src/ is importable when running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pymat import load_all, vis


def _category_hint(material) -> str | None:
    """Infer a mat-vis category from the material's data."""
    # Try the material's TOML key path for hints
    key = getattr(material, "_key", "") or ""
    name = material.name.lower()

    hints = {
        "metal": ["steel", "aluminum", "copper", "brass", "titanium", "tungsten", "lead", "iron"],
        "wood": ["wood", "plywood", "mdf", "balsa"],
        "plastic": ["peek", "delrin", "nylon", "pla", "abs", "petg", "ptfe", "pmma"],
        "ceramic": ["alumina", "macor", "zirconia"],
        "glass": ["glass"],
        "concrete": ["concrete"],
        "stone": ["stone", "rock", "marble", "granite"],
    }

    for category, keywords in hints.items():
        if any(kw in name or kw in key for kw in keywords):
            return category
    return None


def propose_mappings(limit_per_material: int = 3) -> list[dict]:
    """Generate vis mapping proposals for unmapped materials."""
    materials = load_all()
    proposals = []

    for key, mat in materials.items():
        # Skip if already has vis mapping
        if mat.vis.source_id is not None:
            continue

        category = _category_hint(mat)
        pbr = mat.properties.pbr

        try:
            candidates = vis.search(
                category=category,
                roughness=pbr.roughness if pbr.roughness != 0.5 else None,
                metalness=pbr.metallic if pbr.metallic != 0.0 else None,
                limit=limit_per_material,
            )
        except ConnectionError:
            continue

        if not candidates:
            continue

        # Format source_id as "source/id"
        for c in candidates:
            if "source" in c and "id" in c and "/" not in c["id"]:
                c["id"] = f"{c['source']}/{c['id']}"

        proposals.append({
            "material_key": key,
            "material_name": mat.name,
            "category_hint": category,
            "pbr_roughness": pbr.roughness,
            "pbr_metallic": pbr.metallic,
            "candidates": candidates,
        })

    return proposals


def format_toml(proposals: list[dict]) -> str:
    """Format proposals as TOML [vis] sections."""
    lines = ["# Auto-generated vis mapping proposals", "# Review before merging", ""]

    for p in proposals:
        key = p["material_key"]
        top = p["candidates"][0]
        alts = p["candidates"][1:]

        lines.append(f"# {p['material_name']} (category: {p['category_hint']})")
        lines.append(f"# roughness={p['pbr_roughness']}, metallic={p['pbr_metallic']}")
        if alts:
            lines.append(f"# alternatives: {[c['id'] for c in alts]}")
        lines.append(f'[{key}.vis]')
        lines.append(f'default = "auto"')
        lines.append(f'')
        lines.append(f'[{key}.vis.finishes]')
        lines.append(f'auto = "{top["id"]}"')
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "-o", help="Write proposals to file")
    parser.add_argument("--apply", action="store_true", help="Apply top matches (not yet implemented)")
    args = parser.parse_args()

    proposals = propose_mappings()

    if not proposals:
        print("No unmapped materials found (or mat-vis index unavailable)")
        return

    toml_text = format_toml(proposals)

    if args.output:
        Path(args.output).write_text(toml_text)
        print(f"Wrote {len(proposals)} proposals to {args.output}")
    else:
        print(toml_text)
        print(f"\n# {len(proposals)} materials proposed")

    if args.apply:
        print("--apply not yet implemented. Review the proposals and add to TOML manually.")


if __name__ == "__main__":
    main()
