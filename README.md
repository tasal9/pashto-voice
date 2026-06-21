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
- `scripts/load_fleurs_pilot.py` - FLEURS Pashto pilot manifest builder.
- `scripts/pilot_stats.py` - pilot statistics calculator.
- `scripts/inventory_youtube_channel.py` - metadata-only YouTube channel inventory helper; does not download media.
- `scripts/select_youtube_pilot.py` - selects a target-duration YouTube pilot subset after permission.
- `scripts/download_youtube_audio.py` - downloads permitted audio-only YouTube streams.
- `notes/parsvoice_source_summary.md` - concise summary of the attached Persian paper.
- `tmp/pdfs/2510.10774v3.txt` - extracted text from the attached PDF for local reference.

## Working Name

`PashtoVoice` is used as a placeholder corpus name. Rename it before publication if you prefer a Pashto-language name.

## Immediate Next Steps

1. Paste Amin Sultani permission terms into `metadata/permissions/amin_sultani_permission_record.md`.
2. Run a Katib-ASR smoke test on 25-50 Amin Sultani segments.
3. Run resumable Katib-ASR on `metadata/amin_sultani_segments_manifest.jsonl`.
4. Review a sample of ASR transcripts manually and tune segmentation thresholds if needed.
5. Add transcript/text quality scoring after ASR output exists.
6. Expand from the selected 25-video pilot to all permission-covered Amin Sultani videos.
7. Replace remaining paper placeholders after transcription.

## Current Long-Form Pilot Status

- Raw Amin Sultani audio downloaded: 25 `.m4a` files, 8.301 hours.
- Converted WAV audio: 25 files, 16 kHz mono, under `data/processed/youtube_amin_sultani/wav`.
- Segmented audio: 2,317 WAV segments, 8.248 hours, under `data/processed/youtube_amin_sultani/segments`.
- Segment manifest: `metadata/amin_sultani_segments_manifest.jsonl`.
- Audio quality summary: `metadata/amin_sultani_audio_quality_summary.json`.
- Katib-ASR transcription: pending.

## Setup

Install the pilot dependencies before running ASR or dataset scripts:

```bash
python -m pip install -r requirements-pilot.txt
```

The ASR dependencies include `transformers` and `torch`, so the first install can take several minutes.

## Pilot Commands

```bash
python scripts/load_fleurs_pilot.py --config ps_af --split train --target-hours 8 --streaming --out metadata/fleurs_pashto_pilot.jsonl
python scripts/load_fleurs_pilot.py --tsv data/raw/fleurs/ps_af_train.tsv --split train --target-hours 8 --out metadata/fleurs_pashto_pilot.jsonl
python scripts/pilot_stats.py metadata/fleurs_pashto_pilot.jsonl
python scripts/run_katib_asr.py metadata/amin_sultani_segments_manifest.jsonl --limit 25 --device cpu --out metadata/katib_asr_smoke.jsonl --continue-on-error
python scripts/run_katib_asr.py metadata/amin_sultani_segments_manifest.jsonl --resume --out metadata/amin_sultani_katib_asr.jsonl --continue-on-error --progress-every 25
```
