#!/usr/bin/env python3
"""Lightweight health check for a generated MusicQuiz catalog and a sample of previews."""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path


def check_preview(url: str) -> bool:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "MusicQuizCatalogHealth/0.1",
            "Range": "bytes=0-1023",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            status = getattr(response, "status", 200)
            content_type = response.headers.get("Content-Type", "").lower()
            return status in (200, 206) and ("audio" in content_type or "mpeg" in content_type or "octet-stream" in content_type)
    except (urllib.error.URLError, TimeoutError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog")
    parser.add_argument("--sample", type=int, default=8)
    parser.add_argument("--min-tracks", type=int, default=100)
    args = parser.parse_args()

    payload = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    tracks = payload.get("tracks") or []
    if len(tracks) < args.min_tracks:
        raise SystemExit(f"catalog only has {len(tracks)} tracks")
    bad = [track.get("id") for track in tracks if not str(track.get("previewURL", "")).startswith("https://")]
    if bad:
        raise SystemExit(f"catalog contains {len(bad)} invalid preview URLs")

    sample = tracks[: max(0, args.sample)]
    successes = sum(check_preview(track["previewURL"]) for track in sample)
    print(f"catalog schema OK: {len(tracks)} tracks; preview sample reachable: {successes}/{len(sample)}")
    if sample and successes == 0:
        raise SystemExit("no sampled Apple preview URL was reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
