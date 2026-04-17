"""
mat-vis client — thin wrapper around the vendored mat-vis reference client.

The actual fetch logic lives in _vendor_client.py (shipped by mat-vis
as a release asset, vendored here). This module adapts it to pymat's
API surface (module-level functions instead of class methods).

See MorePET/mat#37 for migration context.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pymat.vis._vendor_client import MatVisClient

log = logging.getLogger(__name__)

# Singleton client instance — lazy-initialized
_client: MatVisClient | None = None


def _get_client() -> MatVisClient:
    global _client
    if _client is None:
        _client = MatVisClient()
        # Pre-cache indexes from release assets since they're not in git yet.
        # The vendored client tries raw.githubusercontent.com which 404s.
        # This workaround seeds the cache so the client finds them locally.
        _seed_indexes(_client)
    return _client


def _seed_indexes(client: MatVisClient) -> None:
    """Download index JSONs from release assets into the client's cache.

    Tries the current release tag first, then falls back to older tags.
    Workaround for indexes not being in git yet — they ship as release assets.
    """
    import urllib.request
    from urllib.error import HTTPError, URLError

    manifest = client.manifest
    tag = manifest.get("release_tag", "")
    cache_dir = client._cache_dir / ".indexes"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Collect all sources from manifest + known defaults
    sources = set()
    for tier_data in manifest.get("tiers", {}).values():
        sources.update(tier_data.get("sources", {}).keys())
    sources.add("physicallybased")

    # Tags to try in order (current release, then older)
    tags_to_try = [tag, "v0.1.0"] if tag != "v0.1.0" else [tag]
    base = "https://github.com/MorePET/mat-vis/releases/download"

    for source in sources:
        cache_path = cache_dir / f"{source}.json"
        if cache_path.exists():
            continue
        for t in tags_to_try:
            url = f"{base}/{t}/{source}.json"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "pymat"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = resp.read()
                cache_path.write_bytes(data)
                log.debug("seeded index: %s (from %s)", source, t)
                break
            except (HTTPError, URLError):
                continue
        else:
            log.debug("index not available for %s", source)


def get_manifest(
    release_tag: str | None = None,
) -> dict:
    """Fetch release manifest (URL discovery for all sources × tiers)."""
    client = MatVisClient(tag=release_tag) if release_tag else _get_client()
    return client.manifest


def search(
    *,
    category: str | None = None,
    roughness: float | None = None,
    metalness: float | None = None,
    source: str | None = None,
    tag: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Search the mat-vis index by category and scalar similarity."""
    client = MatVisClient(tag=tag) if tag else _get_client()

    roughness_range = None
    if roughness is not None:
        roughness_range = (max(0.0, roughness - 0.2), min(1.0, roughness + 0.2))

    metalness_range = None
    if metalness is not None:
        metalness_range = (max(0.0, metalness - 0.2), min(1.0, metalness + 0.2))

    results = client.search(
        category=category,
        source=source,
        roughness_range=roughness_range,
        metalness_range=metalness_range,
    )

    # Add score for compatibility with existing callers
    for r in results:
        score = 0.0
        if roughness is not None and r.get("roughness") is not None:
            score += abs(r["roughness"] - roughness)
        if metalness is not None and r.get("metalness") is not None:
            score += abs(r["metalness"] - metalness)
        r["score"] = score

    results.sort(key=lambda r: r["score"])
    return results[:limit]


def fetch(
    source: str,
    material_id: str,
    *,
    tier: str = "1k",
    tag: str | None = None,
    cache: bool = True,
    cache_dir: Path | None = None,
) -> dict[str, bytes]:
    """Fetch textures for a material via rowmap + HTTP range read."""
    client = MatVisClient(tag=tag) if tag else _get_client()
    try:
        return client.fetch_all_textures(source, material_id, tier=tier)
    except Exception as exc:
        log.warning("vis.fetch(%s/%s): %s", source, material_id, exc)
        return {}


def prefetch(
    source: str,
    *,
    tier: str = "1k",
    tag: str | None = None,
    cache_dir: Path | None = None,
) -> int:
    """Download all materials for a source × tier into the local cache."""
    client = MatVisClient(tag=tag) if tag else _get_client()
    return client.prefetch(source, tier=tier)


def rowmap_entry(
    source: str,
    material_id: str,
    *,
    tier: str = "1k",
    tag: str | None = None,
) -> dict[str, dict[str, int]]:
    """Get raw byte-offset info for DIY consumers."""
    client = MatVisClient(tag=tag) if tag else _get_client()
    return client.rowmap_entry(source, material_id, tier=tier)
