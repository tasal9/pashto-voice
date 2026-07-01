#!/usr/bin/env python3
"""Run Katib-ASR on audio files listed in a pilot manifest."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from pashto_normalize import normalize_pashto


ASR_DEPENDENCY_HELP = """Missing ASR dependency: {package}

Install the pilot dependencies with:
    python -m pip install -r requirements-pilot.txt
    python -m pip install -r requirements-asr.txt --retries 10 --timeout 120

Then rerun this command. For long ASR jobs, prefer --resume so completed segments are skipped.
"""


def read_manifest(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def completed_segment_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    completed: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        segment_id = str(row.get("segment_id", "")).strip()
        if segment_id and not row.get("error"):
            completed.add(segment_id)
    return completed


def resolve_audio_path(row: dict[str, Any], *, audio_dir: Path | None, project_root: Path) -> Path:
    filename = row.get("audio_filename") or row.get("audio_path")
    if not filename:
        raise ValueError("Manifest row has neither audio_filename nor audio_path")

    audio_path = Path(str(filename))
    if audio_path.is_absolute():
        return audio_path

    candidates = [audio_path, project_root / audio_path]
    if audio_dir is not None:
        candidates.extend([audio_dir / audio_path, audio_dir / audio_path.name])

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return project_root / audio_path


def output_row(row: dict[str, Any], audio_path: Path, text: str) -> dict[str, Any]:
    reference = str(row.get("transcript", row.get("transcript_raw", "")))
    return {
        "segment_id": row.get("segment_id"),
        "source_id": row.get("source_id"),
        "audio_path": str(audio_path),
        "duration_sec": row.get("duration_sec"),
        "reference": reference,
        "prediction": text,
        "reference_normalized": normalize_pashto(reference, remove_punctuation=True),
        "prediction_normalized": normalize_pashto(text, remove_punctuation=True),
    }


def read_audio_input(audio_path: Path) -> dict[str, Any]:
    import soundfile as sf  # type: ignore[reportMissingImports]

    audio, sampling_rate = sf.read(audio_path, dtype="float32", always_2d=False)
    if isinstance(audio, np.ndarray) and audio.ndim > 1:
        audio = audio.mean(axis=1)
    return {"array": audio, "sampling_rate": sampling_rate}


def resolve_torch_dtype(name: str) -> Any:
    import torch  # type: ignore[reportMissingImports]

    return {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }[name]


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcribe pilot audio with uzair0/Katib-ASR.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--audio-dir", type=Path, help="Optional base directory for manifest audio filenames.")
    parser.add_argument("--project-root", type=Path, help="Project root used to resolve relative audio_path values.")
    parser.add_argument("--out", type=Path, default=Path("metadata/katib_asr_outputs.jsonl"))
    parser.add_argument("--limit", type=int, default=0, help="Optional max rows for smoke tests.")
    parser.add_argument("--resume", action="store_true", help="Append to --out and skip already completed segment_id rows.")
    parser.add_argument("--continue-on-error", action="store_true", help="Write error rows and continue when a segment fails.")
    parser.add_argument("--progress-every", type=int, default=25, help="Print progress every N processed rows.")
    parser.add_argument("--device", default="cuda", help="Use cuda, cpu, or a transformers device index.")
    parser.add_argument(
        "--torch-dtype",
        choices=("float32", "float16", "bfloat16"),
        default="float32",
        help="Torch dtype for model inference. Use float16 or bfloat16 on compatible GPUs.",
    )
    parser.add_argument("--model", default="uzair0/Katib-ASR", help="ASR model checkpoint to load.")
    parser.add_argument(
        "--tokenizer",
        default="openai/whisper-large-v3",
        help="Tokenizer checkpoint to load. Defaults to Whisper large-v3 for compatibility with Katib-ASR.",
    )
    parser.add_argument(
        "--feature-extractor",
        default="openai/whisper-large-v3",
        help="Feature extractor checkpoint to load. Defaults to Whisper large-v3 for compatibility with Katib-ASR.",
    )
    args = parser.parse_args()

    for package in ("transformers", "torch", "soundfile"):
        if importlib.util.find_spec(package) is None:
            parser.exit(1, ASR_DEPENDENCY_HELP.format(package=package))

    from transformers import pipeline  # type: ignore[reportMissingImports]

    asr = pipeline(
        "automatic-speech-recognition",
        model=args.model,
        tokenizer=args.tokenizer,
        feature_extractor=args.feature_extractor,
        torch_dtype=resolve_torch_dtype(args.torch_dtype),
        device=args.device,
        chunk_length_s=30,
    )

    rows = read_manifest(args.manifest)
    if args.limit:
        rows = rows[: args.limit]

    project_root = args.project_root or args.manifest.resolve().parent.parent
    completed = completed_segment_ids(args.out) if args.resume else set()
    if completed:
        rows = [row for row in rows if str(row.get("segment_id", "")).strip() not in completed]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if args.resume else "w"
    start_time = time.time()
    processed = 0
    with args.out.open(mode, encoding="utf-8") as f:
        for row in rows:
            try:
                audio_path = resolve_audio_path(row, audio_dir=args.audio_dir, project_root=project_root)
                result = asr(read_audio_input(audio_path))
                text = result["text"] if isinstance(result, dict) else str(result)
                out = output_row(row, audio_path, text)
            except Exception as exc:
                if not args.continue_on_error:
                    raise
                out = {
                    "segment_id": row.get("segment_id"),
                    "source_id": row.get("source_id"),
                    "audio_path": row.get("audio_path") or row.get("audio_filename"),
                    "error": f"{type(exc).__name__}: {exc}",
                }

            f.write(json.dumps(out, ensure_ascii=False) + "\n")
            f.flush()
            processed += 1
            if args.progress_every and processed % args.progress_every == 0:
                elapsed_min = (time.time() - start_time) / 60
                print(f"Processed {processed}/{len(rows)} rows in {elapsed_min:.1f} min")

    skipped = len(completed) if args.resume else 0
    print(f"Wrote ASR outputs for {processed} manifest rows to {args.out}; skipped {skipped} completed rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
