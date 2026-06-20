#!/usr/bin/env python3
"""Compute WER/CER for ASR JSONL outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pashto_normalize import normalize_pashto


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate ASR predictions with WER/CER.")
    parser.add_argument("asr_outputs", type=Path)
    parser.add_argument("--out", type=Path, default=Path("metadata/asr_eval.json"))
    args = parser.parse_args()

    from jiwer import cer, wer

    rows = [json.loads(line) for line in args.asr_outputs.read_text(encoding="utf-8").splitlines() if line.strip()]
    refs = []
    hyps = []
    for row in rows:
        ref = row.get("reference_normalized") or normalize_pashto(row.get("reference", ""), remove_punctuation=True)
        hyp = row.get("prediction_normalized") or normalize_pashto(row.get("prediction", ""), remove_punctuation=True)
        if ref.strip():
            refs.append(ref)
            hyps.append(hyp)
    result = {
        "rows": len(rows),
        "evaluated_rows": len(refs),
        "wer": round(wer(refs, hyps), 4) if refs else None,
        "cer": round(cer(refs, hyps), 4) if refs else None,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
