"""Shared audio command helpers."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path


DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")


def ffmpeg_exe() -> str:
    env = os.environ.get("FFMPEG_BIN")
    if env:
        return env
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise RuntimeError("ffmpeg not found. Install ffmpeg or imageio-ffmpeg.") from exc


def ffprobe_exe() -> str | None:
    env = os.environ.get("FFPROBE_BIN")
    if env:
        return env
    return shutil.which("ffprobe")


def media_duration(path: Path) -> float:
    ffprobe = ffprobe_exe()
    if ffprobe:
        result = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        return float(result.stdout.strip())

    result = subprocess.run(
        [ffmpeg_exe(), "-hide_banner", "-i", str(path), "-f", "null", "-"],
        text=True,
        capture_output=True,
    )
    match = DURATION_RE.search(result.stderr)
    if not match:
        raise RuntimeError(f"Could not determine media duration for {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
