#!/usr/bin/env python3
"""Compute lightweight audio quality stats for a segment manifest."""

from __future__ import annotations

import argparse
import array
import json
import math
import sys
import wave
from pathlib import Path


def wav_stats(path: Path) -> dict[str, float]:
    with wave.open(str(path), "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        sample_width = wf.getsampwidth()
        channels = wf.getnchannels()
        sample_rate = wf.getframerate()
        frame_count = wf.getnframes()
    if sample_width != 2:
        return {"sample_rate": sample_rate, "channels": channels, "rms_dbfs": -120.0, "peak_dbfs": -120.0, "clipping_ratio": 0.0}
    samples = array.array("h", frames)
    if sys.byteorder == "big":
        samples.byteswap()
    if not samples:
        return {"sample_rate": sample_rate, "channels": channels, "rms_dbfs": -120.0, "peak_dbfs": -120.0, "clipping_ratio": 0.0}
    peak = max(max(samples), -min(samples))
    rms = math.sqrt(sum(x * x for x in samples) / len(samples))
    clipping = sum(1 for x in samples if x >= 32760 or x <= -32760) / len(samples)
    return {
        "sample_rate": sample_rate,
        "channels": channels,
        "frame_count": frame_count,
        "rms_dbfs": round(20 * math.log10(max(rms, 1) / 32768), 3),
        "peak_dbfs": round(20 * math.log10(max(peak, 1) / 32768), 3),
        "clipping_ratio": round(clipping, 6),
    }


def quality_score(row: dict[str, float]) -> float:
    score = 100.0
    duration = float(row.get("duration_sec", 0))
    rms = float(row.get("rms_dbfs", -120))
    clipping = float(row.get("clipping_ratio", 0))
    if duration < 3 or duration > 18:
        score -= 15
    if rms < -35:
        score -= 20
    elif rms < -30:
        score -= 10
    if clipping > 0.01:
        score -= 20
    elif clipping > 0.001:
        score -= 10
    return round(max(0.0, min(100.0, score)), 2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Score WAV segment audio quality.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out", type=Path, default=Path("metadata/audio_quality_scores.jsonl"))
    args = parser.parse_args()

    rows = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as out:
        for row in rows:
            stats = wav_stats(Path(row["audio_path"]))
            merged = {**row, **stats}
            merged["audio_quality_score"] = quality_score(merged)
            out.write(json.dumps(merged, ensure_ascii=False) + "\n")
    print(f"Wrote quality scores for {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
