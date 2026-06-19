# Pilot Run Log

Date: 2026-06-20

## Goal

Run a 5-10 hour Pashto pilot before scaling.

## Selected Pilot Source

FLEURS Pashto (`google/fleurs`, config `ps_af`) was selected for the first technical pilot because it is release-safe for research use under CC-BY-4.0 and has enough Pashto speech for a 5-10 hour smoke test.

## Status

Metadata pilot completed. Audio download and Katib-ASR inference remain pending.

Initial attempts through `datasets.load_dataset("google/fleurs", "ps_af")` and streaming mode stalled before producing rows. The alternative TSV path succeeded:

1. Downloaded `data/ps_af/train.tsv` directly from the FLEURS Hugging Face repository.
2. Built `metadata/fleurs_pashto_pilot.jsonl`.
3. Computed `metadata/pilot_stats.json`.

The direct train audio archive is available but large (`train.tar.gz`, about 1.59 GB in the repo tree; the parquet export route exposed a roughly 1.9 GB file). The local network path was too slow for an interactive download.

## Verified Locally

- Python dependencies installed: `datasets`, `soundfile`, `jiwer`.
- FLEURS Pashto config name confirmed: `ps_af`.
- Pashto normalizer executed successfully.
- Pilot/stat scripts compile successfully.
- Stats pipeline verified with `metadata/sample_manifest.jsonl`.
- FLEURS train metadata downloaded successfully.
- Pilot manifest and statistics generated successfully.

## Pilot Statistics

- Total hours: 8.0
- Segments: 2,265
- Source count: 1
- Total tokens: 58,868
- Unique word forms: 7,692
- Mean segment duration: 12.716 s
- Median segment duration: 11.880 s
- Mean tokens per segment: 25.99
- Mean Pashto character ratio: 0.9998
- Mean Pashto-specific letter coverage: 0.4494
- Gender clip counts: 1,689 male, 576 female

## Next Action

Download the FLEURS Pashto train audio archive on a faster network path, extract it, and run `scripts/run_katib_asr.py` on a small smoke-test subset before scaling to the full 8-hour pilot.

## Amin Sultani Long-Form Pilot

Date: 2026-06-20

The user reported that permission was obtained for the Amin Sultani YouTube channel. A permission record placeholder was created at `metadata/permissions/amin_sultani_permission_record.md`.

Measured source inventory:

- Channel: https://www.youtube.com/@AminSultani10/videos
- Metadata inventory: 73 videos
- Candidate duration: 18.56 hours

Selected/downloaded pilot:

- Pilot manifest: `metadata/amin_sultani_youtube_pilot.jsonl`
- Pilot videos: 25
- Pilot duration: 8.301 hours
- Downloaded audio files: 25
- Local raw audio size: 475 MB
- Local raw audio directory: `data/raw/youtube_amin_sultani/audio`
- Download status: complete
- Format: audio-only `.m4a` streams

Remaining work:

- Install `ffmpeg`.
- Convert raw audio to a consistent WAV format.
- Segment long videos into sentence-like candidate clips.
- Run Katib-ASR transcription.
- Compute ASR/text/audio quality statistics.
