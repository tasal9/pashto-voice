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

The Amin Sultani YouTube channel was approved for the local pilot. Permission records and future permission-request drafts are intentionally not tracked in the public repository.

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

- Run Katib-ASR transcription.
- Compute ASR/text/audio quality statistics.

## Amin Sultani Conversion, Segmentation, And Audio Quality

Date: 2026-06-20

Homebrew ffmpeg installation was blocked by permissions on `/usr/local/share/man/man8`, so the project uses the Python `imageio-ffmpeg` bundled ffmpeg executable.

Completed:

- Converted 25 `.m4a` files to 16 kHz mono WAV.
- WAV directory: `data/processed/youtube_amin_sultani/wav`
- WAV manifest: `metadata/amin_sultani_audio_manifest.jsonl`
- Segmented the WAV files using ffmpeg `silencedetect`.
- Segment directory: `data/processed/youtube_amin_sultani/segments`
- Segment manifest: `metadata/amin_sultani_segments_manifest.jsonl`

Segmentation results:

- Segments: 2,317
- Total segmented duration: 8.248 hours
- Mean segment duration: 12.815 s
- Median segment duration: 14.981 s
- Min/max duration: 3.001 s / 18.000 s

Audio quality summary:

- Mean audio quality score: 99.66
- Median audio quality score: 100.0
- High quality segments (>=90): 2,288
- Acceptable segments (75-89): 29
- Low quality segments (<75): 0
- Mean RMS: -25.203 dBFS
- Segments with clipping: 0

## ASR Environment Check

Date: 2026-06-25

Completed:

- Created a project-local `.venv` because system Python rejects direct package installs under PEP 668.
- Installed pilot and ASR dependencies in `.venv`.
- Pinned ASR requirements to `transformers>=4.38,<4.40` and `numpy<2` so the available local `torch==2.2.2` build can load without the Transformers 5 / NumPy 2 ABI failures.
- Re-ran `tests/test_pipeline.py` successfully in the virtual environment.

ASR smoke-test status:

- `scripts/run_katib_asr.py` now reaches Hugging Face model download.
- First Katib-ASR load starts downloading a 3.09 GB `model.safetensors` file.
- Disabling Xet transfer with `HF_HUB_DISABLE_XET=1` moved the regular Hugging Face cache from metadata-only to about 14 MB, including a partial 10 MB weight download.
- Local download speed was too slow for an interactive run, so transcription was stopped before any ASR rows were written.

Canonical processing order:

1. Finish Katib-ASR transcription for Amin Sultani segments.
2. Run text-quality scoring and manual review on ASR outputs.
3. Use Common Voice and FLEURS for ASR benchmarking and normalization checks.
4. Preserve exact Amin Sultani permission terms before any public release.
5. Request or confirm additional permissions from Books for Afghanistan and Darakht-e Danesh.
6. Scale from the 25-video pilot to all permission-covered Amin Sultani videos.

Next action:

Run the smoke test on a faster network path, preferably with GPU available:

```bash
HF_HUB_DISABLE_XET=1 .venv/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('uzair0/Katib-ASR', allow_patterns=['config.json','generation_config.json','model.safetensors','processor_config.json','tokenizer.json','tokenizer_config.json'], resume_download=True)"
.venv/bin/python scripts/run_katib_asr.py metadata/amin_sultani_segments_manifest.jsonl --limit 25 --device cpu --out metadata/katib_asr_smoke.jsonl --continue-on-error
```

After the smoke test succeeds, run full resumable ASR and text quality scoring:

```bash
.venv/bin/python scripts/run_katib_asr.py metadata/amin_sultani_segments_manifest.jsonl --resume --out metadata/amin_sultani_katib_asr.jsonl --continue-on-error --progress-every 25
.venv/bin/python scripts/text_quality_stats.py metadata/amin_sultani_katib_asr.jsonl --out metadata/amin_sultani_text_quality.jsonl --summary-out metadata/amin_sultani_text_quality_summary.json
.venv/bin/python scripts/export_manual_review.py metadata/amin_sultani_text_quality.jsonl --out metadata/amin_sultani_manual_review.csv --limit 100
```
