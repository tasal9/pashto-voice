#!/usr/bin/env python3
"""Segment long WAV files using ffmpeg silencedetect boundaries."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from audio_tools import ffmpeg_exe, media_duration


SILENCE_START_RE = re.compile(r"silence_start:\s*([0-9.]+)")
SILENCE_END_RE = re.compile(r"silence_end:\s*([0-9.]+)")


def silence_regions(path: Path, noise_db: str, min_silence: float) -> list[tuple[float, float]]:
    result = subprocess.run(
        [
            ffmpeg_exe(),
            "-hide_banner",
            "-i",
            str(path),
            "-af",
            f"silencedetect=noise={noise_db}:d={min_silence}",
            "-f",
            "null",
            "-",
        ],
        text=True,
        capture_output=True,
    )
    current_start: float | None = None
    regions: list[tuple[float, float]] = []
    for line in result.stderr.splitlines():
        start_match = SILENCE_START_RE.search(line)
        if start_match:
            current_start = float(start_match.group(1))
            continue
        end_match = SILENCE_END_RE.search(line)
        if end_match and current_start is not None:
            regions.append((current_start, float(end_match.group(1))))
            current_start = None
    return regions


def candidate_segments(duration: float, silences: list[tuple[float, float]], min_duration: float, max_duration: float) -> list[tuple[float, float]]:
    boundaries = [0.0]
    for start, end in silences:
        midpoint = (start + end) / 2.0
        if 0 < midpoint < duration:
            boundaries.append(midpoint)
    boundaries.append(duration)
    boundaries = sorted(set(round(b, 3) for b in boundaries))

    segments: list[tuple[float, float]] = []
    current = boundaries[0]
    for boundary in boundaries[1:]:
        span = boundary - current
        if span < min_duration:
            continue
        if span <= max_duration:
            segments.append((current, boundary))
            current = boundary
        else:
            split = current
            while boundary - split > max_duration:
                segments.append((split, split + max_duration))
                split += max_duration
            if boundary - split >= min_duration:
                segments.append((split, boundary))
            current = boundary
    return [(round(s, 3), round(e, 3)) for s, e in segments if e - s >= min_duration]


def cut_segment(src: Path, dst: Path, start: float, end: float) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            ffmpeg_exe(),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-to",
            f"{end:.3f}",
            "-i",
            str(src),
            "-c",
            "copy",
            str(dst),
        ],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Segment WAV audio using silence-based VAD.")
    parser.add_argument("manifest", type=Path, help="Audio manifest from convert_audio_to_wav.py.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/youtube_amin_sultani/segments"))
    parser.add_argument("--out", type=Path, default=Path("metadata/amin_sultani_segments_manifest.jsonl"))
    parser.add_argument("--noise-db", default="-35dB")
    parser.add_argument("--min-silence", type=float, default=0.45)
    parser.add_argument("--min-duration", type=float, default=3.0)
    parser.add_argument("--max-duration", type=float, default=18.0)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    rows = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.limit:
        rows = rows[: args.limit]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    total_segments = 0
    total_hours = 0.0
    with args.out.open("w", encoding="utf-8") as out:
        for row in rows:
            src = Path(row["audio_path"])
            duration = float(row.get("duration_sec") or media_duration(src))
            regions = silence_regions(src, args.noise_db, args.min_silence)
            segments = candidate_segments(duration, regions, args.min_duration, args.max_duration)
            for idx, (start, end) in enumerate(segments):
                segment_id = f"{row['audio_id']}_{idx:05d}"
                dst = args.output_dir / row["audio_id"] / f"{segment_id}.wav"
                cut_segment(src, dst, start, end)
                segment_row = {
                    "segment_id": segment_id,
                    "source_id": row["source_id"],
                    "audio_id": row["audio_id"],
                    "audio_path": str(dst),
                    "source_audio_path": str(src),
                    "start_time_sec": start,
                    "end_time_sec": end,
                    "duration_sec": round(end - start, 3),
                    "segmentation_method": "ffmpeg_silencedetect",
                    "noise_db": args.noise_db,
                    "min_silence_sec": args.min_silence,
                }
                out.write(json.dumps(segment_row, ensure_ascii=False) + "\n")
                total_segments += 1
                total_hours += end - start

    print(f"Wrote {total_segments} segments ({total_hours / 3600:.3f} h) to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
