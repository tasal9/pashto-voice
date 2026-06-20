# PashtoVoice Research

This workspace starts a Pashto adaptation of the ParsVoice-style corpus paper and dataset pipeline.

## Goal

Create a large-scale, multi-speaker Pashto speech-text corpus suitable for text-to-speech (TTS), ASR, speech-text alignment, punctuation restoration, and low-resource Pashto speech-language research.

## Current Artifacts

- `paper/pashtovoice_draft.md` - first research-paper draft modeled on the ParsVoice structure, rewritten for Pashto.
- `docs/pashto_pipeline_plan.md` - implementation plan for building the corpus.
- `docs/source_selection.md` - selected and deferred Pashto audio sources with licensing notes.
- `docs/asr_baseline.md` - selected baseline ASR model and evaluation plan.
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

## Immediate Next Steps

1. Paste Amin Sultani permission terms into `metadata/permissions/amin_sultani_permission_record.md`.
2. Run Katib-ASR on `metadata/amin_sultani_segments_manifest.jsonl`.
3. Review a sample of ASR transcripts manually and tune segmentation thresholds if needed.
4. Add transcript/text quality scoring after ASR output exists.
5. Replace remaining paper placeholders after transcription.

## Current Long-Form Pilot Status

- Raw Amin Sultani audio downloaded: 25 `.m4a` files, 8.301 hours.
- Converted WAV audio: 25 files, 16 kHz mono, under `data/processed/youtube_amin_sultani/wav`.
- Segmented audio: 2,317 WAV segments, 8.248 hours, under `data/processed/youtube_amin_sultani/segments`.
- Segment manifest: `metadata/amin_sultani_segments_manifest.jsonl`.
- Audio quality summary: `metadata/amin_sultani_audio_quality_summary.json`.
- Katib-ASR transcription: pending.

## Pilot Commands

```bash
/Users/yaqoobtasal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/load_fleurs_pilot.py --config ps_af --split train --target-hours 8 --streaming --out metadata/fleurs_pashto_pilot.jsonl
/Users/yaqoobtasal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/load_fleurs_pilot.py --tsv data/raw/fleurs/ps_af_train.tsv --split train --target-hours 8 --out metadata/fleurs_pashto_pilot.jsonl
/Users/yaqoobtasal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/pilot_stats.py metadata/fleurs_pashto_pilot.jsonl
```

## Testing

To verify the correctness of the pipeline components (normalization maps, audio quality calculations, and pilot statistics), run the test suite:

```bash
python3 tests/test_pipeline.py
```
