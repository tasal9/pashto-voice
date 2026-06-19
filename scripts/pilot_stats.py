#!/usr/bin/env python3
"""Compute PashtoVoice pilot statistics from a JSONL or CSV manifest."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path
from typing import Any

from pashto_normalize import normalize_pashto, pashto_character_ratio, pashto_specific_coverage


def read_manifest(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def compute_stats(rows: list[dict[str, Any]], transcript_field: str = "transcript") -> dict[str, Any]:
    durations = [as_float(r.get("duration_sec")) for r in rows]
    normalized = [normalize_pashto(str(r.get(transcript_field, ""))) for r in rows]
    tokenized = [txt.split() for txt in normalized]
    tokens = [tok for toks in tokenized for tok in toks]
    speakers = {str(r.get("speaker_id", "")).strip() for r in rows if str(r.get("speaker_id", "")).strip()}
    sources = {str(r.get("source_id", "")).strip() for r in rows if str(r.get("source_id", "")).strip()}
    genders: dict[str, int] = {}
    for row in rows:
        gender = str(row.get("gender", "")).strip().lower() or "unknown"
        genders[gender] = genders.get(gender, 0) + 1
    char_ratios = [pashto_character_ratio(txt) for txt in normalized if txt]
    coverage_scores = [pashto_specific_coverage(txt) for txt in normalized if txt]

    total_seconds = sum(durations)
    return {
        "total_hours": round(total_seconds / 3600, 3),
        "segments": len(rows),
        "speakers": len(speakers) if speakers else None,
        "sources": len(sources) if sources else None,
        "total_tokens": len(tokens),
        "unique_word_forms": len(set(tokens)),
        "mean_segment_duration_sec": round(statistics.mean(durations), 3) if durations else 0,
        "median_segment_duration_sec": round(statistics.median(durations), 3) if durations else 0,
        "mean_tokens_per_segment": round(statistics.mean(len(t) for t in tokenized), 3) if rows else 0,
        "mean_pashto_character_ratio": round(statistics.mean(char_ratios), 4) if char_ratios else 0,
        "mean_pashto_specific_letter_coverage": round(statistics.mean(coverage_scores), 4) if coverage_scores else 0,
        "gender_clip_counts": dict(sorted(genders.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute pilot corpus statistics.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--transcript-field", default="transcript")
    parser.add_argument("--out", type=Path, default=Path("metadata/pilot_stats.json"))
    args = parser.parse_args()

    rows = read_manifest(args.manifest)
    stats = compute_stats(rows, transcript_field=args.transcript_field)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
