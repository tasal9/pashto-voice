#!/usr/bin/env python3
"""Package a PashtoVoice Common Voice-style corpus into a release archive."""

from __future__ import annotations

import argparse
import json
import shutil
import tarfile
import tempfile
from pathlib import Path
from typing import Any

from validate_common_voice import validate_corpus


def package_corpus(
    corpus_dir: Path,
    out_path: Path,
    *,
    require_audio: bool = False,
    archive_format: str = "gztar",
) -> dict[str, Any]:
    validation = validate_corpus(corpus_dir, require_audio=require_audio)
    if not validation["valid"]:
        return {"success": False, "validation": validation}

    out_path.parent.mkdir(parents=True, exist_ok=True)

    if archive_format == "gztar":
        suffix = ".tar.gz"
        mode = "w:gz"
    elif archive_format == "zip":
        suffix = ".zip"
        mode = "zip"
    else:
        raise ValueError(f"Unsupported archive format: {archive_format}")

    if not str(out_path).endswith(suffix):
        out_path = out_path.with_suffix(suffix)

    with tempfile.TemporaryDirectory() as tmpdir:
        staged = Path(tmpdir) / corpus_dir.name
        shutil.copytree(corpus_dir, staged)
        if archive_format == "zip":
            shutil.make_archive(str(out_path.with_suffix("")), "zip", root_dir=tmpdir, base_dir=corpus_dir.name)
        else:
            with tarfile.open(out_path, mode) as tar:
                tar.add(staged, arcname=corpus_dir.name)

    return {
        "success": True,
        "archive": str(out_path),
        "validation": validation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a Common Voice-style corpus.")
    parser.add_argument("corpus_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("dist/pashtovoice_commonvoice.tar.gz"))
    parser.add_argument("--require-audio", action="store_true")
    parser.add_argument("--format", choices=("gztar", "zip"), default="gztar")
    args = parser.parse_args()

    result = package_corpus(args.corpus_dir, args.out, require_audio=args.require_audio, archive_format=args.format)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
