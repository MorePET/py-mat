#!/usr/bin/env python3
"""mat-vis reference client — pure Python, zero dependencies.

Fetches PBR textures from mat-vis GitHub Releases via HTTP range reads.
Uses only urllib (stdlib). No pyarrow, no binary deps.

Usage as library:
    from mat_vis_client import MatVisClient
    client = MatVisClient()
    png_bytes = client.fetch_texture("ambientcg", "Rock064", "color", tier="1k")

    # Search by category and scalar ranges
    results = client.search("metal", roughness_range=(0.2, 0.6))

    # Bulk prefetch all materials for offline use
    client.prefetch("ambientcg", tier="1k")

Usage as CLI:
    python mat_vis_client.py list                              # list sources × tiers
    python mat_vis_client.py materials ambientcg 1k            # list materials
    python mat_vis_client.py fetch ambientcg Rock064 color 1k  # fetch PNG → stdout
    python mat_vis_client.py fetch ambientcg Rock064 color 1k -o rock.png
    python mat_vis_client.py search metal --roughness 0.2:0.6  # search materials
    python mat_vis_client.py prefetch ambientcg 1k             # bulk download
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

REPO = "MorePET/mat-vis"
GITHUB_RELEASES = f"https://github.com/{REPO}/releases"
GITHUB_RAW = f"https://raw.githubusercontent.com/{REPO}"
LATEST_MANIFEST_URL = f"{GITHUB_RELEASES}/latest/download/release-manifest.json"
DEFAULT_CACHE_DIR = Path(os.environ.get("MAT_VIS_CACHE", Path.home() / ".cache" / "mat-vis"))
USER_AGENT = "mat-vis-client/0.2 (Python)"

# Valid categories per index-schema.json
CATEGORIES = frozenset(
    [
        "metal",
        "wood",
        "stone",
        "fabric",
        "plastic",
        "concrete",
        "ceramic",
        "glass",
        "organic",
        "other",
    ]
)


def _get(url: str, headers: dict | None = None) -> bytes:
    """HTTP GET with User-Agent."""
    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _get_json(url: str) -> dict | list:
    """Fetch and parse JSON."""
    return json.loads(_get(url))


def _in_range(value: float | None, lo: float, hi: float) -> bool:
    """Check if a value falls within [lo, hi]. None values never match."""
    if value is None:
        return False
    return lo <= value <= hi


class MatVisClient:
    """Lightweight client for mat-vis texture data."""

    def __init__(
        self,
        *,
        manifest_url: str | None = None,
        cache_dir: Path | None = None,
        tag: str | None = None,
    ):
        self._cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self._manifest: dict | None = None
        self._rowmaps: dict[str, dict] = {}
        self._indexes: dict[str, list[dict]] = {}
        self._tag = tag

        if manifest_url:
            self._manifest_url = manifest_url
        elif tag:
            self._manifest_url = f"{GITHUB_RELEASES}/download/{tag}/release-manifest.json"
        else:
            self._manifest_url = LATEST_MANIFEST_URL

    @property
    def manifest(self) -> dict:
        """Fetch and cache the release manifest."""
        if self._manifest is None:
            cache_path = self._cache_dir / ".manifest.json"
            if cache_path.exists():
                self._manifest = json.loads(cache_path.read_text())
            else:
                self._manifest = _get_json(self._manifest_url)
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(json.dumps(self._manifest, indent=2))
        return self._manifest

    def sources(self, tier: str = "1k") -> list[str]:
        """List available sources for a tier."""
        tier_data = self.manifest.get("tiers", {}).get(tier, {})
        return list(tier_data.get("sources", {}).keys())

    def tiers(self) -> list[str]:
        """List available tiers."""
        return list(self.manifest.get("tiers", {}).keys())

    def rowmap(self, source: str, tier: str, category: str | None = None) -> dict:
        """Fetch and cache rowmaps. Merges partitioned rowmaps into one."""
        key = f"{source}-{tier}-{category or 'all'}"
        if key not in self._rowmaps:
            tier_data = self.manifest["tiers"][tier]
            base_url = tier_data["base_url"]
            src_data = tier_data["sources"][source]

            rowmap_files = src_data.get("rowmap_files", [])
            if not rowmap_files:
                rowmap_file = src_data.get("rowmap_file", f"{source}-{tier}-rowmap.json")
                rowmap_files = [rowmap_file]

            if category:
                rowmap_files = [f for f in rowmap_files if category in f] or rowmap_files[:1]

            # Fetch all partition rowmaps and merge materials
            merged: dict = {"materials": {}}
            for rmf in rowmap_files:
                cache_path = self._cache_dir / ".rowmaps" / rmf
                if cache_path.exists():
                    rm = json.loads(cache_path.read_text())
                else:
                    url = base_url + rmf
                    rm = _get_json(url)
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    cache_path.write_text(json.dumps(rm, indent=2))

                # Each partitioned rowmap has its own parquet_file
                pq_file = rm.get("parquet_file", "")
                for mid, channels in rm.get("materials", {}).items():
                    # Tag each channel with its parquet file for range reads
                    for ch_data in channels.values():
                        ch_data["parquet_file"] = pq_file
                    merged["materials"][mid] = channels

                # Keep metadata from last rowmap (they're all the same except materials)
                for k in ("version", "release_tag", "source", "tier"):
                    if k in rm:
                        merged[k] = rm[k]

            self._rowmaps[key] = merged

        return self._rowmaps[key]

    def materials(self, source: str, tier: str) -> list[str]:
        """List material IDs available for a source × tier."""
        rm = self.rowmap(source, tier)
        return sorted(rm.get("materials", {}).keys())

    def channels(self, source: str, material_id: str, tier: str) -> list[str]:
        """List channels available for a material."""
        rm = self.rowmap(source, tier)
        mat = rm.get("materials", {}).get(material_id, {})
        return sorted(mat.keys())

    # ── Index & search ──────────────────────────────────────────

    def _index_url(self, source: str) -> str:
        """Build the URL for a source's index JSON."""
        ref = self._tag or "main"
        return f"{GITHUB_RAW}/{ref}/index/{source}.json"

    def index(self, source: str) -> list[dict]:
        """Fetch and cache the material index for a source.

        Returns a list of material entries per index-schema.json.
        """
        if source not in self._indexes:
            cache_path = self._cache_dir / ".indexes" / f"{source}.json"
            if cache_path.exists():
                self._indexes[source] = json.loads(cache_path.read_text())
            else:
                url = self._index_url(source)
                self._indexes[source] = _get_json(url)
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(json.dumps(self._indexes[source], indent=2))
        return self._indexes[source]

    def search(
        self,
        category: str | None = None,
        *,
        roughness_range: tuple[float, float] | None = None,
        metalness_range: tuple[float, float] | None = None,
        source: str | None = None,
        tier: str = "1k",
    ) -> list[dict]:
        """Search materials by category and scalar ranges.

        Fetches index JSON for the given source (or all sources for the
        tier) and filters locally. Returns matching index entries.

        Args:
            category: Filter by material category (e.g. "metal", "wood").
            roughness_range: (min, max) roughness filter, inclusive.
            metalness_range: (min, max) metalness filter, inclusive.
            source: Limit search to one source. If None, searches all
                    sources available for the given tier.
            tier: Only return materials that have this tier available.
        """
        if category and category not in CATEGORIES:
            raise ValueError(
                f"Unknown category {category!r}. Valid: {', '.join(sorted(CATEGORIES))}"
            )

        sources = [source] if source else self.sources(tier)
        results: list[dict] = []

        for src in sources:
            for entry in self.index(src):
                if category and entry.get("category") != category:
                    continue
                if roughness_range and not _in_range(entry.get("roughness"), *roughness_range):
                    continue
                if metalness_range and not _in_range(entry.get("metalness"), *metalness_range):
                    continue
                if tier not in entry.get("available_tiers", []):
                    continue
                results.append(entry)

        return results

    # ── Bulk operations ─────────────────────────────────────────

    def fetch_all_textures(
        self,
        source: str,
        material_id: str,
        tier: str = "1k",
    ) -> dict[str, bytes]:
        """Fetch all texture channels for a material.

        Returns a dict mapping channel name to PNG bytes.
        """
        chs = self.channels(source, material_id, tier)
        return {ch: self.fetch_texture(source, material_id, ch, tier) for ch in chs}

    def prefetch(
        self,
        source: str,
        tier: str = "1k",
        *,
        on_progress: callable | None = None,
    ) -> int:
        """Bulk download all materials for a source + tier to cache.

        Args:
            source: Source name (e.g. "ambientcg").
            tier: Resolution tier (default "1k").
            on_progress: Optional callback(material_id, index, total).

        Returns the number of materials fetched.
        """
        mat_ids = self.materials(source, tier)
        total = len(mat_ids)

        for i, mid in enumerate(mat_ids):
            self.fetch_all_textures(source, mid, tier)
            if on_progress:
                on_progress(mid, i + 1, total)

        return total

    def rowmap_entry(
        self,
        source: str,
        material_id: str,
        tier: str = "1k",
    ) -> dict[str, dict]:
        """Get raw rowmap offsets for a material (for DIY consumers).

        Returns a dict of channel -> {offset, length, parquet_file}.
        """
        rm = self.rowmap(source, tier)
        mat = rm["materials"][material_id]
        parquet_file = rm["parquet_file"]
        return {
            ch: {"offset": info["offset"], "length": info["length"], "parquet_file": parquet_file}
            for ch, info in mat.items()
        }

    def fetch_texture(
        self,
        source: str,
        material_id: str,
        channel: str,
        tier: str = "1k",
    ) -> bytes:
        """Fetch a single texture PNG via HTTP range read.

        Returns raw PNG bytes. Caches locally.
        """
        # Check cache first
        cache_path = self._cache_dir / source / tier / material_id / f"{channel}.png"
        if cache_path.exists():
            return cache_path.read_bytes()

        # Find in rowmap
        rm = self.rowmap(source, tier)
        mat = rm["materials"][material_id]
        rng = mat[channel]
        offset = rng["offset"]
        length = rng["length"]

        # Find parquet URL (per-partition from merged rowmap)
        tier_data = self.manifest["tiers"][tier]
        base_url = tier_data["base_url"]
        parquet_file = rng.get("parquet_file") or rm.get("parquet_file", "")
        url = base_url + parquet_file

        # HTTP range read
        range_header = f"bytes={offset}-{offset + length - 1}"
        data = _get(url, headers={"Range": range_header})

        # Verify PNG
        if data[:4] != b"\x89PNG":
            raise ValueError(f"Expected PNG, got {data[:4]!r}")

        # Cache
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(data)

        return data


# ── CLI ─────────────────────────────────────────────────────────


def _parse_range(s: str) -> tuple[float, float]:
    """Parse 'lo:hi' into a (lo, hi) tuple."""
    parts = s.split(":")
    if len(parts) != 2:
        raise ValueError(f"Expected lo:hi, got {s!r}")
    return float(parts[0]), float(parts[1])


def main():
    import argparse

    parser = argparse.ArgumentParser(prog="mat-vis-client", description="mat-vis texture client")
    parser.add_argument("--tag", help="Release tag (default: latest)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List sources x tiers")

    p_mat = sub.add_parser("materials", help="List materials for a source x tier")
    p_mat.add_argument("source")
    p_mat.add_argument("tier", nargs="?", default="1k")

    p_fetch = sub.add_parser("fetch", help="Fetch a texture PNG")
    p_fetch.add_argument("source")
    p_fetch.add_argument("material")
    p_fetch.add_argument("channel")
    p_fetch.add_argument("tier", nargs="?", default="1k")
    p_fetch.add_argument("-o", "--output", help="Output file (default: stdout)")

    p_search = sub.add_parser("search", help="Search materials by category / scalars")
    p_search.add_argument("category", nargs="?", help="Category filter (e.g. metal, wood)")
    p_search.add_argument("--source", help="Limit to one source")
    p_search.add_argument("--tier", default="1k")
    p_search.add_argument("--roughness", help="Roughness range as lo:hi")
    p_search.add_argument("--metalness", help="Metalness range as lo:hi")

    p_prefetch = sub.add_parser("prefetch", help="Bulk download all materials for source x tier")
    p_prefetch.add_argument("source")
    p_prefetch.add_argument("tier", nargs="?", default="1k")

    args = parser.parse_args()
    client = MatVisClient(tag=args.tag)

    if args.cmd == "list":
        for tier in client.tiers():
            sources = client.sources(tier)
            print(f"{tier}: {', '.join(sources)}")

    elif args.cmd == "materials":
        for mid in client.materials(args.source, args.tier):
            print(mid)

    elif args.cmd == "fetch":
        data = client.fetch_texture(args.source, args.material, args.channel, args.tier)
        if args.output:
            Path(args.output).write_bytes(data)
            print(f"Wrote {args.output} ({len(data):,} bytes)", file=sys.stderr)
        else:
            sys.stdout.buffer.write(data)

    elif args.cmd == "search":
        roughness = _parse_range(args.roughness) if args.roughness else None
        metalness = _parse_range(args.metalness) if args.metalness else None
        results = client.search(
            args.category,
            roughness_range=roughness,
            metalness_range=metalness,
            source=args.source,
            tier=args.tier,
        )
        for entry in results:
            scalars = []
            if entry.get("roughness") is not None:
                scalars.append(f"R={entry['roughness']:.2f}")
            if entry.get("metalness") is not None:
                scalars.append(f"M={entry['metalness']:.2f}")
            scalar_str = f" ({', '.join(scalars)})" if scalars else ""
            print(f"{entry['source']}/{entry['id']}  [{entry.get('category', '?')}]{scalar_str}")
        print(f"\n{len(results)} result(s)", file=sys.stderr)

    elif args.cmd == "prefetch":

        def _progress(mid: str, i: int, total: int) -> None:
            print(f"[{i}/{total}] {mid}", file=sys.stderr)

        n = client.prefetch(args.source, args.tier, on_progress=_progress)
        print(f"Prefetched {n} materials", file=sys.stderr)


if __name__ == "__main__":
    main()
