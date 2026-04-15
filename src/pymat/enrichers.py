"""
Material enrichment from external data sources.

Currently supports:
- periodictable: NIST element and compound data
- Future: Materials Project API, MatWeb scraping, etc.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .core import Material

logger = logging.getLogger(__name__)


def enrich_from_periodictable(material: Material) -> Material:
    """
    Fill in missing material properties from the `periodictable` library.

    Uses the material's chemical formula to populate:

    - `composition` — element → atom count, derived from the formula
    - `density` — ONLY for pure elements. `periodictable` does not provide
      compound densities (a compound's density depends on crystal packing
      and cannot be derived from formula alone). For compounds, enrich
      density via `enrich_from_matproj` instead.

    Molar mass is NOT set here — it is available at any time via the
    computed `Material.molar_mass` property. See ADR-0001.

    Args:
        material: Material instance to enrich.

    Returns:
        The enriched material (modified in-place).

    Example:
        iron = Material("Iron", formula="Fe")
        enrich_from_periodictable(iron)
        print(iron.density)        # 7.874 (element lookup)
        print(iron.molar_mass)     # 55.85 (computed from formula)

        lyso = Material("LYSO", formula="Lu1.8Y0.2SiO5")
        enrich_from_periodictable(lyso)
        print(lyso.composition)    # {'Lu': 1.8, 'Y': 0.2, 'Si': 1, 'O': 5}
        print(lyso.molar_mass)     # 440.87
        print(lyso.density)        # None — use enrich_from_matproj for this
    """
    if not material.formula:
        return material

    try:
        import periodictable as pt
    except ImportError as e:
        raise ImportError(
            "periodictable not installed. Install with: pip install periodictable"
        ) from e

    try:
        formula = pt.formula(material.formula)
    except Exception as e:
        logger.warning("Could not parse formula %r: %s", material.formula, e)
        return material

    # Density: only pure elements have a meaningful density in periodictable.
    # For compounds `formula.density` is None, so this is a no-op — do not
    # fake compound density by averaging element densities (physically wrong).
    if not material.properties.mechanical.density and formula.density:
        material.properties.mechanical.density = formula.density

    # Composition: element -> atom count (not mass fraction).
    if not material.composition and formula.atoms:
        material.composition = {str(el): count for el, count in formula.atoms.items()}

    return material


def enrich_from_matproj(
    material: Material,
    api_key: str,
    properties: list[str] | None = None,
) -> Material:
    """
    Fetch properties from Materials Project API.

    Requires a free API key from https://materialsproject.org/

    Args:
        material: Material instance to enrich
        api_key: Materials Project API key
        properties: List of properties to fetch (default: common ones)

    Returns:
        The enriched material (modified in-place)

    Example:
        al2o3 = Material("Alumina", formula="Al2O3")
        enrich_from_matproj(al2o3, api_key="YOUR_KEY")
        print(al2o3.properties.mechanical.density)
    """
    if not material.formula:
        return material

    try:
        from pymatgen.ext.matproj import MPRester
    except ImportError as e:
        raise ImportError("pymatgen not installed. Install with: pip install pymatgen") from e

    if properties is None:
        properties = [
            "density",
            "band_gap",
            "formation_energy",
            "material_id",
        ]

    try:
        with MPRester(api_key) as mpr:
            results = mpr.summary.search(
                formula=material.formula,
                fields=properties,
            )

            if results:
                result = results[0]  # Take most stable phase

                if "density" in result:
                    material.properties.mechanical.density = result["density"]

                # Store other properties in custom dict
                for key, value in result.items():
                    if key not in ("density",):
                        material.properties.custom[key] = value

    except Exception as e:
        print(f"Warning: Materials Project query failed: {e}")

    return material


def enrich_all(
    material: Material,
    use_periodictable: bool = True,
    matproj_api_key: Optional[str] = None,
) -> Material:
    """
    Enrich material from all available sources.

    Args:
        material: Material to enrich
        use_periodictable: Whether to query periodictable (default: True)
        matproj_api_key: Materials Project API key (optional)

    Returns:
        The enriched material
    """
    if use_periodictable:
        enrich_from_periodictable(material)

    if matproj_api_key:
        enrich_from_matproj(material, matproj_api_key)

    return material
