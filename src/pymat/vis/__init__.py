"""
Visual material data from mat-vis.

Public API — all functions importable from `pymat.vis` directly:

    from pymat import vis

    vis.search(category="metal", roughness=0.3)
    vis.fetch("ambientcg", "Metal032", tier="1k")
    vis.prefetch("ambientcg", tier="1k")
    vis.get_manifest()
    vis.rowmap_entry("ambientcg", "Metal032", tier="1k")

Powered by mat-vis-client (installed separately or from git).
Material.vis wires into this module for lazy texture loading.
"""

from mat_vis_client import (
    fetch,
    get_manifest,
    prefetch,
    rowmap_entry,
    search,
)

__all__ = [
    "search",
    "fetch",
    "prefetch",
    "rowmap_entry",
    "get_manifest",
]
