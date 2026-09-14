#!/usr/bin/env python3
"""Build the public MusicQuiz catalog from Apple's public iTunes Search API."""
from __future__ import annotations

import argparse
import json
import random
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SEARCH_URL = "https://itunes.apple.com/search"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}

REJECT = re.compile(
    r"\b(live|instrumental|inst\.?|karaoke|remix(?:es)?|acoustic|demo|nightcore|sped\s*up|slowed)\b|"
    r"\b(japanese|english|chinese|korean|jp|kr|cn)\s*(?:ver\.?|version)\b|"
    r"\b(radio|club|dance|extended)\s*(?:edit|mix|version)\b|"
    r"\bremaster(?:ed)?\b",
    re.I,
)
CREDIT_SPLIT = re.compile(r"\s*(?:&|,|;|/|\bfeat\.?\b|\bfeaturing\b|\bwith\b|\bvs\.?\b)\s*", re.I)
TRAILING_PAREN = re.compile(r"\s*\([^()]*\)\s*$")


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^a-z0-9가-힣]+", "", value)


def artist_match(result_artist: str, target: str) -> bool:
    target_key = norm(target)
    if not target_key:
        return False
    candidates = {result_artist, TRAILING_PAREN.sub("", result_artist)}
    for candidate in list(candidates):
        candidates.update(part for part in CREDIT_SPLIT.split(candidate) if part)
        if not re.search(r"(?:^|\s)x(?:\s|$)", target, re.I):
            candidates.update(part for part in re.split(r"(?:^|\s)x(?:\s|$)", candidate, flags=re.I) if part)
    normalized_target = unicodedata.normalize("NFKC", target).strip().casefold()
    for candidate in candidates:
        if norm(candidate) == target_key:
            return True
        normalized_candidate = unicodedata.normalize("NFKC", candidate).strip().casefold()
        if normalized_candidate.startswith(normalized_target + "-"):
            return True
    return False


def retry_delay(error: urllib.error.HTTPError, attempt: int) -> float:
    retry_after = error.headers.get("Retry-After") if error.headers else None
    if retry_after:
        try:
            return min(float(retry_after), 30.0)
        except ValueError:
            pass
    return min(2 ** attempt, 16) + random.uniform(0.1, 0.8)


def search_artist(artist: str, country: str = "us", limit: int = 200, retries: int = 5) -> list[dict]:
    query = urllib.parse.urlencode({
        "term": artist,
        "entity": "song",
        "media": "music",
        "country": country,
        "limit": limit,
    })
    req = urllib.request.Request(
        f"{SEARCH_URL}?{query}",
        headers={"User-Agent": "MusicQuizCatalog/0.3"},
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=25) as response:
                return json.load(response).get("results", [])
        except urllib.error.HTTPError as error:
            if error.code not in RETRYABLE_STATUS or attempt >= retries:
                raise
            delay = retry_delay(error, attempt)
            print(f"retrying {artist!r} after HTTP {error.code} in {delay:.1f}s")
            time.sleep(delay)
        except (urllib.error.URLError, TimeoutError):
            if attempt >= retries:
                raise
            delay = min(2 ** attempt, 16) + random.uniform(0.1, 0.8)
            print(f"retrying {artist!r} after network error in {delay:.1f}s")
            time.sleep(delay)
    return []


def keep(item: dict, artist: str) -> bool:
    title = item.get("trackName") or ""
    preview = item.get("previewUrl") or ""
    return bool(
        preview.startswith("https://")
        and title
        and not REJECT.search(title)
        and artist_match(item.get("artistName") or "", artist)
    )


def clean_title(raw: str) -> str:
    value = raw.strip()
    value = re.sub(
        r"\s*[\[(](?:single|album|explicit|clean)?\s*(?:version|ver\.)?[\])]\s*$",
        "",
        value,
        flags=re.I,
    )
    return value.strip()


def read_artists(path: str) -> list[str]:
    artists: list[str] = []
    seen: set[str] = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key = norm(line)
        if key and key not in seen:
            seen.add(key)
            artists.append(line)
    return artists


def build_catalog(artists: list[str], country: str, max_per_artist: int) -> dict:
    dedupe: dict[tuple[str, str], dict] = {}
    per_artist: dict[str, int] = {}
    for artist in artists:
        accepted = 0
        for item in search_artist(artist, country):
            if not keep(item, artist):
                continue
            title = clean_title(item["trackName"])
            key = (norm(item.get("artistName") or artist), norm(title))
            if not key[1]:
                continue
            candidate = {
                "id": f"apple-{item['trackId']}",
                "title": title,
                "artist": item.get("artistName") or artist,
                "source": "apple_preview",
                "previewURL": item["previewUrl"],
                "storeURL": item.get("trackViewUrl"),
                "artworkURL": item.get("artworkUrl100"),
                "releaseDate": (item.get("releaseDate") or "")[:10] or None,
                "providerTrackID": str(item["trackId"]),
            }
            old = dedupe.get(key)
            if old is None or (candidate["releaseDate"] or "") > (old["releaseDate"] or ""):
                dedupe[key] = candidate
            accepted += 1
            if accepted >= max_per_artist:
                break
        per_artist[artist] = accepted
        time.sleep(0.35 + random.uniform(0.0, 0.25))
    tracks = sorted(dedupe.values(), key=lambda x: (norm(x["artist"]), norm(x["title"]), x["id"]))
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "tracks": tracks,
        "stats": {"artists": len(artists), "tracks": len(tracks), "acceptedByArtist": per_artist},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artists-file", required=True)
    parser.add_argument("--country", default="us")
    parser.add_argument("--max-per-artist", type=int, default=40)
    parser.add_argument("--min-tracks", type=int, default=100)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    artists = read_artists(args.artists_file)
    payload = build_catalog(artists, args.country, args.max_per_artist)
    if len(payload["tracks"]) < args.min_tracks:
        raise SystemExit(f"catalog too small: {len(payload['tracks'])} tracks < minimum {args.min_tracks}")
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(payload['tracks'])} tracks from {len(artists)} artists -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
