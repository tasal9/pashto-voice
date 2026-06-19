#!/usr/bin/env python3
"""Inventory a YouTube channel without downloading media."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect YouTube channel video metadata with yt-dlp.")
    parser.add_argument("url", help="YouTube channel/videos URL.")
    parser.add_argument("--out", type=Path, default=Path("metadata/youtube_inventory.jsonl"))
    parser.add_argument("--limit", type=int, default=0, help="Optional max videos to keep.")
    args = parser.parse_args()

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-single-json",
        "--skip-download",
        args.url,
    ]
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    data = json.loads(result.stdout)
    entries = data.get("entries") or []
    if args.limit:
        entries = entries[: args.limit]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for entry in entries:
            row = {
                "source_id": "youtube_amin_sultani",
                "video_id": entry.get("id"),
                "title": entry.get("title"),
                "url": entry.get("url") or entry.get("webpage_url"),
                "duration_sec": entry.get("duration"),
                "channel": entry.get("channel") or data.get("channel") or data.get("uploader"),
                "license_status": "permission_required",
                "download_allowed": False,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {len(entries)} metadata rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
