#!/usr/bin/env python3
"""Create a 5-10 hour Pashto FLEURS pilot manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Load FLEURS Pashto and write a pilot JSONL manifest.")
    parser.add_argument("--config", default="ps_af", help="FLEURS config, expected Pashto is usually ps_af.")
    parser.add_argument("--split", default="train")
    parser.add_argument("--target-hours", type=float, default=8.0)
    parser.add_argument("--out", type=Path, default=Path("metadata/fleurs_pashto_pilot.jsonl"))
    parser.add_argument("--streaming", action="store_true", help="Stream rows instead of caching full parquet files.")
    args = parser.parse_args()

    from datasets import Audio, load_dataset

    dataset = load_dataset("google/fleurs", args.config, split=args.split, streaming=args.streaming)
    dataset = dataset.cast_column("audio", Audio(decode=False))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    total_sec = 0.0
    count = 0
    with args.out.open("w", encoding="utf-8") as f:
        for row in dataset:
            duration = float(row.get("num_samples", 0)) / float(row.get("sample_rate", 16000) or 16000)
            item = {
                "segment_id": f"fleurs_{args.split}_{row.get('id', count)}",
                "source_id": "google_fleurs_ps_af",
                "duration_sec": round(duration, 3),
                "transcript": row.get("transcription") or row.get("raw_transcription") or "",
                "speaker_id": "",
                "license": "cc-by-4.0",
                "split": args.split,
            }
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            total_sec += duration
            count += 1
            if total_sec >= args.target_hours * 3600:
                break

    print(f"Wrote {count} rows, {total_sec / 3600:.3f} hours to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
