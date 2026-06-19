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
- `scripts/load_fleurs_pilot.py` - FLEURS Pashto pilot manifest builder.
- `scripts/pilot_stats.py` - pilot statistics calculator.
- `notes/parsvoice_source_summary.md` - concise summary of the attached Persian paper.
- `tmp/pdfs/2510.10774v3.txt` - extracted text from the attached PDF for local reference.

## Working Name

`PashtoVoice` is used as a placeholder corpus name. Rename it before publication if you prefer a Pashto-language name.

## Immediate Next Steps

1. Download the FLEURS Pashto train audio archive on a faster network path and extract it locally.
2. Send the permission requests in `docs/permission_request_books_for_afghanistan.md` and `docs/permission_request_darakht_e_danesh.md`.
3. Run Katib-ASR on the pilot manifest once audio is locally available.
4. Replace remaining long-form corpus placeholders after a permitted audiobook source is processed.

## Pilot Commands

```bash
/Users/yaqoobtasal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/load_fleurs_pilot.py --config ps_af --split train --target-hours 8 --streaming --out metadata/fleurs_pashto_pilot.jsonl
/Users/yaqoobtasal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/load_fleurs_pilot.py --tsv data/raw/fleurs/ps_af_train.tsv --split train --target-hours 8 --out metadata/fleurs_pashto_pilot.jsonl
/Users/yaqoobtasal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/pilot_stats.py metadata/fleurs_pashto_pilot.jsonl
```
