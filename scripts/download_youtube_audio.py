#!/usr/bin/env python3
"""Download audio-only streams for a permitted YouTube pilot manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Download YouTube audio listed in a JSONL manifest.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("data/raw/youtube_amin_sultani/audio"))
    parser.add_argument("--archive", type=Path, default=Path("data/raw/youtube_amin_sultani/downloaded.txt"))
    parser.add_argument("--limit", type=int, default=0, help="Optional max videos for smoke tests.")
    args = parser.parse_args()

    rows = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [row for row in rows if row.get("download_allowed")]
    if args.limit:
        rows = rows[: args.limit]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.archive.parent.mkdir(parents=True, exist_ok=True)

    for row in rows:
        url = row.get("url")
        if not url:
            continue
        video_id = row.get("video_id") or "%(id)s"
        output_template = str(args.out_dir / f"{video_id}.%(ext)s")
        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--ignore-errors",
            "--download-archive",
            str(args.archive),
            "-f",
            "bestaudio[ext=m4a]/bestaudio/best",
            "-o",
            output_template,
            url,
        ]
        subprocess.run(cmd, check=True)

    print(f"Processed {len(rows)} permitted videos into {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
