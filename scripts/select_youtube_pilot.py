#!/usr/bin/env python3
"""Select a target-duration pilot subset from a YouTube inventory JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Select YouTube videos up to a target duration.")
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--target-hours", type=float, default=8.0)
    parser.add_argument("--out", type=Path, default=Path("metadata/amin_sultani_youtube_pilot.jsonl"))
    args = parser.parse_args()

    rows = [json.loads(line) for line in args.inventory.read_text(encoding="utf-8").splitlines() if line.strip()]
    selected = []
    total_sec = 0.0
    target_sec = args.target_hours * 3600
    for row in rows:
        duration = float(row.get("duration_sec") or 0)
        if duration <= 0:
            continue
        item = dict(row)
        item["license_status"] = "permission_granted_user_reported"
        item["download_allowed"] = True
        item["permission_date"] = "2026-06-20"
        item["split"] = "pilot"
        selected.append(item)
        total_sec += duration
        if total_sec >= target_sec:
            break

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for row in selected:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {len(selected)} videos, {total_sec / 3600:.3f} hours to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
