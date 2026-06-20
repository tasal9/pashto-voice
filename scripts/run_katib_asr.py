#!/usr/bin/env python3
"""Run Katib-ASR on audio files listed in a pilot manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pashto_normalize import normalize_pashto


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcribe pilot audio with uzair0/Katib-ASR.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--audio-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("metadata/katib_asr_outputs.jsonl"))
    parser.add_argument("--limit", type=int, default=0, help="Optional max rows for smoke tests.")
    parser.add_argument("--device", default="cuda", help="Use cuda, cpu, or a transformers device index.")
    args = parser.parse_args()

    from transformers import pipeline

    asr = pipeline(
        "automatic-speech-recognition",
        model="uzair0/Katib-ASR",
        torch_dtype="auto",
        device=args.device,
        chunk_length_s=30,
    )

    rows = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.limit:
        rows = rows[: args.limit]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for row in rows:
            filename = row.get("audio_filename") or row.get("audio_path")
            if not filename:
                continue
            audio_path = Path(filename)
            if not audio_path.is_absolute() and not audio_path.exists():
                audio_path = args.audio_dir / filename
            result = asr(str(audio_path))
            text = result["text"] if isinstance(result, dict) else str(result)
            out = {
                "segment_id": row.get("segment_id"),
                "audio_path": str(audio_path),
                "reference": row.get("transcript", ""),
                "prediction": text,
                "reference_normalized": normalize_pashto(row.get("transcript", ""), remove_punctuation=True),
                "prediction_normalized": normalize_pashto(text, remove_punctuation=True),
            }
            f.write(json.dumps(out, ensure_ascii=False) + "\n")

    print(f"Wrote ASR outputs for {len(rows)} manifest rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
