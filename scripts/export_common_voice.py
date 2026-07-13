#!/usr/bin/env python3
"""Export PashtoVoice manifests to a Mozilla Common Voice-style corpus package."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from pashto_normalize import normalize_pashto


COMMON_VOICE_COLUMNS = [
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


LOOKUP_DIRS = [
    Path("data/processed/youtube_amin_sultani/segments"),
    Path("data/processed"),
    Path("data/raw"),
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_number} of {path}: {exc}") from exc
    return rows


def load_asr_index(asr_paths: list[Path] | None) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    if not asr_paths:
        return index
    for path in asr_paths:
        for row in read_jsonl(path):
            segment_id = str(row.get("segment_id", "")).strip()
            if segment_id and not row.get("error"):
                index[segment_id] = row
    return index


def load_quality_index(quality_path: Path | None) -> dict[str, dict[str, Any]]:
    if not quality_path:
        return {}
    return {
        str(row.get("segment_id", "")).strip(): row
        for row in read_jsonl(quality_path)
        if str(row.get("segment_id", "")).strip()
    }


def find_audio_file(audio_path: str, *, audio_root: Path | None, project_root: Path) -> Path | None:
    """Resolve an audio path from the manifest to an existing file."""
    rel = Path(audio_path)
    candidates = [rel]
    if audio_root is not None:
        candidates.append(audio_root / rel)
    candidates.append(project_root / rel)
    for base in LOOKUP_DIRS:
        candidates.append(project_root / base / rel.name)
        candidates.append(project_root / base / rel)
        if rel.parts:
            candidates.append(project_root / base / "/".join(rel.parts[-2:]))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def rebased_clip_path(audio_path: str) -> Path:
    """Rebase a project audio path to the Common Voice clips/ layout."""
    parts = Path(audio_path).parts
    # Try to detect <source>/segments/<audio_id>/<segment_id>.wav layout.
    if "segments" in parts:
        seg_idx = parts.index("segments")
        return Path(*parts[seg_idx + 1 :])
    # Fall back to filename only under a generic pashtovoice/ folder.
    return Path("pashtovoice") / Path(audio_path).name


def pick_transcript(
    row: dict[str, Any], asr_row: dict[str, Any] | None
) -> tuple[str, str]:
    """Return (sentence, sentence_normalized) from the best available source."""
    text_sources = []
    if asr_row is not None:
        text_sources.extend(
            [asr_row.get("prediction"), asr_row.get("transcript"), asr_row.get("reference")]
        )
    text_sources.extend(
        [row.get("transcript"), row.get("transcript_raw"), row.get("transcript_punctuated")]
    )
    for text in text_sources:
        text = str(text).strip() if text is not None else ""
        if text:
            normalized = normalize_pashto(text, remove_punctuation=False)
            return text, normalized
    return "", ""


def build_common_voice_row(
    row: dict[str, Any],
    asr_index: dict[str, dict[str, Any]],
    quality_index: dict[str, dict[str, Any]],
    locale: str,
) -> dict[str, Any]:
    segment_id = str(row.get("segment_id", "")).strip()
    asr_row = asr_index.get(segment_id)
    quality_row = quality_index.get(segment_id)

    sentence, sentence_normalized = pick_transcript(row, asr_row)

    audio_quality_score = float(
        (quality_row or {}).get("audio_quality_score", row.get("audio_quality_score", 0)) or 0
    )
    text_quality_score = float(
        (quality_row or {}).get("text_quality_score", row.get("text_quality_score", 0)) or 0
    )

    audio_path = str(row.get("audio_path") or row.get("audio_filename") or "")
    rebased = rebased_clip_path(audio_path)

    return {
        "path": str(rebased),
        "sentence": sentence,
        "sentence_normalized": sentence_normalized,
        "up_votes": 0,
        "down_votes": 0,
        "age": str(row.get("age", "")).strip(),
        "gender": str(row.get("gender", "")).strip(),
        "accent": str(row.get("dialect", "")).strip(),
        "locale": locale,
        "segment_id": segment_id,
        "source_id": str(row.get("source_id", "")).strip(),
        "audio_id": str(row.get("audio_id", "")).strip(),
        "start_time_sec": row.get("start_time_sec", ""),
        "end_time_sec": row.get("end_time_sec", ""),
        "duration_sec": row.get("duration_sec", ""),
        "audio_quality_score": audio_quality_score,
        "text_quality_score": text_quality_score,
        "speaker_id": str(row.get("speaker_id", "")).strip(),
        "split": str(row.get("split", "")).strip(),
    }


def classify_validation(row: dict[str, Any]) -> str:
    score = float(row.get("audio_quality_score", 0) or 0)
    if score >= 90:
        return "validated"
    if score >= 75:
        return "other"
    return "invalidated"


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COMMON_VOICE_COLUMNS, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in COMMON_VOICE_COLUMNS})


def copy_clips(
    rows: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
    clips_dir: Path,
    *,
    audio_root: Path | None,
    project_root: Path,
    symlink: bool,
) -> tuple[int, int]:
    """Copy or symlink audio files into clips/. Returns (copied, missing)."""
    source_by_segment = {str(r.get("segment_id", "")).strip(): r for r in source_rows}
    copied = 0
    missing = 0
    for row in rows:
        segment_id = str(row.get("segment_id", "")).strip()
        source_row = source_by_segment.get(segment_id, {})
        audio_path = str(source_row.get("audio_path") or source_row.get("audio_filename") or "")
        if not audio_path:
            missing += 1
            continue
        source_file = find_audio_file(audio_path, audio_root=audio_root, project_root=project_root)
        if source_file is None:
            missing += 1
            continue
        dest = clips_dir / row["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        if symlink:
            if dest.exists() or dest.is_symlink():
                dest.unlink()
            dest.symlink_to(source_file.resolve())
        else:
            shutil.copy2(source_file, dest)
        copied += 1
    return copied, missing


def write_readme(out_dir: Path, stats: dict[str, Any], args: argparse.Namespace) -> None:
    validated = stats.get("validated", 0)
    other = stats.get("other", 0)
    invalidated = stats.get("invalidated", 0)
    total = validated + other + invalidated
    readme = f"""# PashtoVoice Common Voice-Style Corpus

A Pashto speech-text corpus packaged in a Mozilla Common Voice-compatible format.

## Release Snapshot

| Split | Clips |
| --- | --- |
| validated | {validated} |
| other (needs review) | {other} |
| invalidated | {invalidated} |
| **Total** | **{total}** |

## Quick Start

Each TSV file is UTF-8 encoded and tab-separated with a header row.
Audio clips live under `clips/` and are referenced by the `path` column.

```python
import pandas as pd
validated = pd.read_csv("validated.tsv", sep="\t")
```

## Fields

See `docs/common_voice_format.md` in the source repository for the full schema and validation rules.

## Source

Primary source: `{args.source_name or "youtube_amin_sultani"}`
Locale: `{args.locale}`

## Notes and Known Limitations

- Manual Common Voice up/down votes are not yet collected. Validation status is derived from automated audio quality scores.
- Transcripts are populated from ASR outputs when available. Segments without ASR output have empty `sentence` fields and require transcription.
- Please review licensing and permission records before redistributing derived audio or text.

## Citation

See `CITATION.bib`.
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")


def write_citation(out_dir: Path, source_name: str) -> None:
    citation = f"""@dataset{{pashtovoice_commonvoice,
  title = {{PashtoVoice: A Common Voice-Style Pashto Speech-Text Corpus}},
  author = {{PashtoVoice Contributors}},
  year = {{2026}},
  publisher = {{GitHub}},
  howpublished = {{\\url{{https://github.com/tasal9/pashto-voice-research}}}},
  note = {{Primary source: {source_name}}}
}}
"""
    (out_dir / "CITATION.bib").write_text(citation, encoding="utf-8")


def write_license(out_dir: Path, license_text: str | None) -> None:
    text = license_text or (
        "This corpus is released under terms compatible with the source audio and text licenses. "
        "Verify source-level licensing and permission records before redistribution. "
        "When contributing clips back to Mozilla Common Voice, CC0-1.0 applies."
    )
    (out_dir / "LICENSE.md").write_text(text + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export PashtoVoice manifests to a Common Voice-style corpus package."
    )
    parser.add_argument("manifest", type=Path, help="Segment manifest JSONL.")
    parser.add_argument("--out-dir", type=Path, default=Path("pashtovoice_commonvoice"))
    parser.add_argument("--asr", type=Path, action="append", help="Optional ASR output JSONL(s).")
    parser.add_argument("--quality", type=Path, help="Optional audio quality scores JSONL.")
    parser.add_argument("--audio-root", type=Path, help="Root directory for resolving audio paths.")
    parser.add_argument("--project-root", type=Path, help="Project root for fallback path resolution.")
    parser.add_argument("--copy-audio", action="store_true", help="Copy audio files into clips/.")
    parser.add_argument("--symlink-audio", action="store_true", help="Symlink audio files into clips/.")
    parser.add_argument("--locale", default="ps", help="BCP-47 locale code.")
    parser.add_argument("--source-name", help="Human-readable source name for documentation.")
    parser.add_argument("--license-text", help="License text to write into LICENSE.md.")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"Manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    project_root = args.project_root or args.manifest.resolve().parent.parent

    source_rows = read_jsonl(args.manifest)
    if not source_rows:
        print("Manifest is empty.", file=sys.stderr)
        return 1

    asr_index = load_asr_index(args.asr)
    quality_index = load_quality_index(args.quality)

    cv_rows = [
        build_common_voice_row(row, asr_index, quality_index, args.locale)
        for row in source_rows
    ]

    splits: dict[str, list[dict[str, Any]]] = {"validated": [], "other": [], "invalidated": []}
    for row in cv_rows:
        splits[classify_validation(row)].append(row)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    clips_dir = args.out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    for split_name, rows in splits.items():
        write_tsv(args.out_dir / f"{split_name}.tsv", rows)

    # Empty reported.tsv with the same schema.
    write_tsv(args.out_dir / "reported.tsv", [])

    stats = {name: len(rows) for name, rows in splits.items()}
    stats["total"] = sum(stats.values())
    stats["with_transcript"] = sum(1 for row in cv_rows if row["sentence"].strip())
    stats["without_transcript"] = stats["total"] - stats["with_transcript"]
    stats["clips_copied"] = 0
    stats["clips_missing"] = 0

    if args.copy_audio or args.symlink_audio:
        copied, missing = copy_clips(
            cv_rows,
            source_rows,
            clips_dir,
            audio_root=args.audio_root,
            project_root=project_root,
            symlink=args.symlink_audio,
        )
        stats["clips_copied"] = copied
        stats["clips_missing"] = missing

    write_readme(args.out_dir, stats, args)
    write_citation(args.out_dir, args.source_name or "youtube_amin_sultani")
    write_license(args.out_dir, args.license_text)

    stats_path = args.out_dir / "corpus_stats.json"
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
