#!/usr/bin/env python3
"""Validate a PashtoVoice Common Voice-style corpus package."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


EXPECTED_FILES = ["validated.tsv", "other.tsv", "invalidated.tsv", "reported.tsv", "README.md"]
EXPECTED_COLUMNS = [
    "path",
    "sentence",
    "sentence_normalized",
    "up_votes",
    "down_votes",
    "age",
    "gender",
    "accent",
    "locale",
    "segment_id",
    "source_id",
    "audio_id",
    "start_time_sec",
    "end_time_sec",
    "duration_sec",
    "audio_quality_score",
    "text_quality_score",
    "speaker_id",
    "split",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def validate_corpus(corpus_dir: Path, *, require_audio: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for name in EXPECTED_FILES:
        if not (corpus_dir / name).exists():
            errors.append(f"Missing required file: {name}")

    all_rows: list[dict[str, str]] = []
    for tsv_name in ["validated.tsv", "other.tsv", "invalidated.tsv", "reported.tsv"]:
        tsv_path = corpus_dir / tsv_name
        if not tsv_path.exists():
            continue
        rows = read_tsv(tsv_path)
        all_rows.extend(rows)
        if not rows and tsv_name == "reported.tsv":
            continue
        if not rows:
            warnings.append(f"{tsv_name} is empty")
            continue
        missing_cols = [col for col in EXPECTED_COLUMNS if col not in rows[0]]
        if missing_cols:
            errors.append(f"{tsv_name} missing columns: {', '.join(missing_cols)}")
        for idx, row in enumerate(rows, start=2):
            if not row.get("path"):
                errors.append(f"{tsv_name}:{idx}: empty path")
            if not row.get("segment_id"):
                errors.append(f"{tsv_name}:{idx}: empty segment_id")
            if row.get("locale") and row.get("locale") != "ps":
                warnings.append(f"{tsv_name}:{idx}: locale is not 'ps': {row.get('locale')}")
            try:
                duration = float(row.get("duration_sec", "") or 0)
                if duration <= 0:
                    errors.append(f"{tsv_name}:{idx}: non-positive duration")
            except ValueError:
                errors.append(f"{tsv_name}:{idx}: invalid duration")
            audio_path = corpus_dir / "clips" / row.get("path", "")
            if require_audio and not audio_path.exists():
                errors.append(f"{tsv_name}:{idx}: audio missing: {row.get('path')}")
            elif not require_audio and not audio_path.exists():
                warnings.append(f"{tsv_name}:{idx}: audio missing: {row.get('path')}")

    segment_ids = [row.get("segment_id", "") for row in all_rows if row.get("segment_id")]
    if len(segment_ids) != len(set(segment_ids)):
        duplicates = {sid for sid in segment_ids if segment_ids.count(sid) > 1}
        errors.append(f"Duplicate segment_ids: {', '.join(sorted(duplicates))[:5]}")

    # Summarize repeated warnings to keep reports readable.
    missing_audio_count = sum(1 for w in warnings if "audio missing" in w)
    if missing_audio_count:
        warnings = [w for w in warnings if "audio missing" not in w]
        warnings.append(f"{missing_audio_count} rows reference missing audio files under clips/")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "total_rows": len(all_rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Common Voice-style corpus package.")
    parser.add_argument("corpus_dir", type=Path)
    parser.add_argument("--require-audio", action="store_true", help="Require every clip file to exist.")
    parser.add_argument("--out", type=Path, help="Optional JSON validation report path.")
    args = parser.parse_args()

    result = validate_corpus(args.corpus_dir, require_audio=args.require_audio)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.out:
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
