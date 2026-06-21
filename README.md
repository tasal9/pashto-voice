# PashtoVoice Research

This workspace starts a Pashto adaptation of the ParsVoice-style corpus paper and dataset pipeline.

## Goal

Create a large-scale, multi-speaker Pashto speech-text corpus suitable for text-to-speech (TTS), ASR, speech-text alignment, punctuation restoration, and low-resource Pashto speech-language research.

## Current Artifacts

- `paper/pashtovoice_draft.md` - first research-paper draft modeled on the ParsVoice structure, rewritten for Pashto.
- `docs/pashto_pipeline_plan.md` - implementation plan for building the corpus.
- `docs/source_selection.md` - selected and deferred Pashto audio sources with licensing notes.
- `docs/asr_baseline.md` - selected baseline ASR model and evaluation plan.
- `docs/scale_up_roadmap.md` - staged roadmap for growing the corpus beyond the current pilot.
- `metadata/schema.md` - proposed release metadata schema.
- `scripts/pashto_normalize.py` - Pashto Arabic-script normalization utility.
- `scripts/audio_quality_stats.py` - Optimized WAV audio quality stats computer (peak, RMS, clipping, scoring).
- `scripts/load_fleurs_pilot.py` - FLEURS Pashto pilot manifest builder.
- `scripts/pilot_stats.py` - pilot statistics calculator.
- `scripts/inventory_youtube_channel.py` - metadata-only YouTube channel inventory helper; does not download media.
- `scripts/select_youtube_pilot.py` - selects a target-duration YouTube pilot subset after permission.
- `scripts/download_youtube_audio.py` - downloads permitted audio-only YouTube streams.
- `tests/test_pipeline.py` - Unit and integration tests for normalization, stats, and audio scoring.
- `notes/parsvoice_source_summary.md` - concise summary of the attached Persian paper.
- `tmp/pdfs/2510.10774v3.txt` - extracted text from the attached PDF for local reference.

## Working Name

`PashtoVoice` is used as a placeholder corpus name. Rename it before publication if you prefer a Pashto-language name.

## Current Long-Form Pilot Status

- Raw Amin Sultani audio downloaded: 25 `.m4a` files, 8.301 hours.
- Converted WAV audio: 25 files, 16 kHz mono, under `data/processed/youtube_amin_sultani/wav`.
- Segmented audio: 2,317 WAV segments, 8.248 hours, under `data/processed/youtube_amin_sultani/segments`.
- Segment manifest: `metadata/amin_sultani_segments_manifest.jsonl`.
- Audio quality summary: `metadata/amin_sultani_audio_quality_summary.json`.
- Katib-ASR transcription: pending.

## Setup

Install the lightweight pilot dependencies before running dataset, inventory, quality, or test scripts:

```bash
python -m pip install -r requirements-pilot.txt
```

Install the ASR dependencies before running Katib-ASR:

```bash
python -m pip install -r requirements-asr.txt --retries 10 --timeout 120
```

The ASR dependencies include `transformers` and `torch`, so the first install can take several minutes and may need a stable network connection.

## Pilot Commands

```bash
python scripts/load_fleurs_pilot.py --config ps_af --split train --target-hours 8 --streaming --out metadata/fleurs_pashto_pilot.jsonl
python scripts/load_fleurs_pilot.py --tsv data/raw/fleurs/ps_af_train.tsv --split train --target-hours 8 --out metadata/fleurs_pashto_pilot.jsonl
python scripts/pilot_stats.py metadata/fleurs_pashto_pilot.jsonl
python scripts/run_katib_asr.py metadata/amin_sultani_segments_manifest.jsonl --limit 25 --device cpu --out metadata/katib_asr_smoke.jsonl --continue-on-error
python scripts/run_katib_asr.py metadata/amin_sultani_segments_manifest.jsonl --resume --out metadata/amin_sultani_katib_asr.jsonl --continue-on-error --progress-every 25
```

## Testing

To verify the correctness of the pipeline components (normalization maps, audio quality calculations, and pilot statistics), run the test suite:

```bash
python3 tests/test_pipeline.py
```
