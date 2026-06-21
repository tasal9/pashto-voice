#!/usr/bin/env python3
"""Score Pashto transcript quality for JSONL manifests or ASR outputs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from pashto_normalize import normalize_pashto, pashto_character_ratio, pashto_specific_coverage


DEFAULT_TEXT_FIELDS = ("prediction", "transcript", "transcript_raw", "reference")

COMMON_PASHTO_WORDS = {
    "او",
    "د",
    "په",
    "ته",
    "چې",
    "چي",
    "له",
    "دا",
    "دی",
    "ده",
    "کې",
    "کي",
    "نه",
    "یو",
    "هم",
}


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


def pick_text(row: dict[str, Any], fields: tuple[str, ...]) -> tuple[str, str]:
    for field in fields:
        value = str(row.get(field, "")).strip()
        if value:
            return field, value
    return fields[0], ""


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def length_quality(token_count: int) -> float:
    if token_count == 0:
        return 0.0
    if 4 <= token_count <= 28:
        return 1.0
    if token_count < 4:
        return token_count / 4.0
    return clamp(1.0 - ((token_count - 28) / 42.0))


def repetition_quality(tokens: list[str]) -> float:
    if not tokens:
        return 0.0
    counts = Counter(tokens)
    repeated_tokens = sum(count - 1 for count in counts.values() if count > 1)
    unique_ratio = len(counts) / len(tokens)
    return clamp((unique_ratio * 0.7) + ((1.0 - repeated_tokens / len(tokens)) * 0.3))


def complexity_quality(tokens: list[str]) -> float:
    if not tokens:
        return 0.0
    mean_word_length = sum(len(token) for token in tokens) / len(tokens)
    length_component = clamp(mean_word_length / 6.0)
    common_ratio = sum(1 for token in tokens if token in COMMON_PASHTO_WORDS) / len(tokens)
    common_component = 1.0 - abs(common_ratio - 0.25) / 0.75
    return clamp((length_component * 0.55) + (common_component * 0.45))


def score_text(text: str) -> dict[str, Any]:
    normalized = normalize_pashto(text)
    tokens = normalized.split()
    character_quality = pashto_character_ratio(normalized)
    metrics = {
        "transcript_normalized": normalized,
        "token_count": len(tokens),
        "character_quality": round(character_quality, 4),
        "length_quality": round(length_quality(len(tokens)), 4),
        "repetition_quality": round(repetition_quality(tokens), 4),
        "complexity_quality": round(complexity_quality(tokens), 4),
        "pashto_letter_coverage": round(pashto_specific_coverage(normalized), 4),
    }
    score = (
        metrics["character_quality"] * 0.25
        + metrics["length_quality"] * 0.20
        + metrics["repetition_quality"] * 0.20
        + metrics["complexity_quality"] * 0.175
        + metrics["pashto_letter_coverage"] * 0.175
    )
    metrics["text_quality_score"] = round(score, 4)
    return metrics


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [float(row["text_quality_score"]) for row in rows if "text_quality_score" in row]
    if not scores:
        return {"rows": len(rows), "scored_rows": 0}
    sorted_scores = sorted(scores)
    midpoint = len(sorted_scores) // 2
    median = sorted_scores[midpoint] if len(sorted_scores) % 2 else (sorted_scores[midpoint - 1] + sorted_scores[midpoint]) / 2
    return {
        "rows": len(rows),
        "scored_rows": len(scores),
        "mean_text_quality_score": round(sum(scores) / len(scores), 4),
        "median_text_quality_score": round(median, 4),
        "min_text_quality_score": round(min(scores), 4),
        "max_text_quality_score": round(max(scores), 4),
        "high_quality_rows": sum(1 for score in scores if score >= 0.80),
        "review_rows": sum(1 for score in scores if 0.60 <= score < 0.80),
        "low_quality_rows": sum(1 for score in scores if score < 0.60),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Add Pashto text-quality scores to a JSONL manifest or ASR output.")
    parser.add_argument("input", type=Path, help="Input JSONL file.")
    parser.add_argument("--out", type=Path, required=True, help="Scored JSONL output path.")
    parser.add_argument("--summary-out", type=Path, help="Optional JSON summary path.")
    parser.add_argument("--text-field", action="append", help="Preferred text field. Can be repeated.")
    args = parser.parse_args()

    fields = tuple(args.text_field) if args.text_field else DEFAULT_TEXT_FIELDS
    rows = read_jsonl(args.input)
    scored_rows: list[dict[str, Any]] = []
    for row in rows:
        text_field, text = pick_text(row, fields)
        scored_row = dict(row)
        scored_row["text_quality_source_field"] = text_field
        scored_row.update(score_text(text))
        scored_rows.append(scored_row)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for row in scored_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = summarize(scored_rows)
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())