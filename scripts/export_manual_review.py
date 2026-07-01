#!/usr/bin/env python3
"""Export a focused manual-review CSV from scored ASR JSONL rows."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REVIEW_COLUMNS = [
    "review_status",
    "reviewer_notes",
    "corrected_transcript",
    "segment_id",
    "source_id",
    "audio_path",
    "duration_sec",
    "text_quality_score",
    "prediction",
    "prediction_normalized",
    "reference",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"Line {line_number} is not a JSON object")
        rows.append(row)
    return rows


def review_priority(row: dict[str, Any]) -> tuple[int, float, str]:
    score = float(row.get("text_quality_score", 0.0) or 0.0)
    if score < 0.60:
        bucket = 0
    elif score < 0.80:
        bucket = 1
    else:
        bucket = 2
    return bucket, score, str(row.get("segment_id", ""))


def select_review_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=review_priority)
    return ordered[:limit] if limit else ordered


def review_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "review_status": "pending",
        "reviewer_notes": "",
        "corrected_transcript": "",
        "segment_id": row.get("segment_id", ""),
        "source_id": row.get("source_id", ""),
        "audio_path": row.get("audio_path", ""),
        "duration_sec": row.get("duration_sec", ""),
        "text_quality_score": row.get("text_quality_score", ""),
        "prediction": row.get("prediction", ""),
        "prediction_normalized": row.get("prediction_normalized") or row.get("transcript_normalized", ""),
        "reference": row.get("reference", ""),
    }


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(review_row(row))


def main() -> int:
    parser = argparse.ArgumentParser(description="Export ASR/text-quality rows for manual review.")
    parser.add_argument("input", type=Path, help="Scored ASR JSONL input.")
    parser.add_argument("--out", type=Path, required=True, help="Manual-review CSV output path.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum rows to export; use 0 for all rows.")
    args = parser.parse_args()

    rows = read_jsonl(args.input)
    selected = select_review_rows(rows, args.limit)
    write_csv(selected, args.out)
    print(f"Wrote {len(selected)} review rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
