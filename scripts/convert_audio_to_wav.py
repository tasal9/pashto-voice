#!/usr/bin/env python3
"""Convert raw audio files to 16 kHz mono WAV and write an audio manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from audio_tools import ffmpeg_exe, media_duration


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert audio files to normalized WAV.")
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/youtube_amin_sultani/audio"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/youtube_amin_sultani/wav"))
    parser.add_argument("--manifest", type=Path, default=Path("metadata/amin_sultani_audio_manifest.jsonl"))
    parser.add_argument("--source-id", default="youtube_amin_sultani")
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    files = sorted(args.input_dir.glob("*"))
    files = [p for p in files if p.is_file() and p.suffix.lower() in {".m4a", ".mp3", ".wav", ".webm", ".opus"}]
    if args.limit:
        files = files[: args.limit]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)

    with args.manifest.open("w", encoding="utf-8") as out:
        for src in files:
            wav = args.output_dir / f"{src.stem}.wav"
            cmd = [
                ffmpeg_exe(),
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(src),
                "-ac",
                "1",
                "-ar",
                str(args.sample_rate),
                "-sample_fmt",
                "s16",
                str(wav),
            ]
            subprocess.run(cmd, check=True)
            duration = media_duration(wav)
            row = {
                "source_id": args.source_id,
                "audio_id": src.stem,
                "raw_audio_path": str(src),
                "audio_path": str(wav),
                "duration_sec": round(duration, 3),
                "sample_rate": args.sample_rate,
                "channels": 1,
                "format": "wav_s16le",
            }
            out.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Converted {len(files)} files to {args.output_dir}")
    print(f"Wrote manifest to {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
