# PashtoVoice Research

This workspace starts a Pashto adaptation of the ParsVoice-style corpus paper and dataset pipeline.

## Goal

Create a large-scale, multi-speaker Pashto speech-text corpus suitable for text-to-speech (TTS), ASR, speech-text alignment, punctuation restoration, and low-resource Pashto speech-language research.

## Current Artifacts

- `paper/pashtovoice_draft.md` - first research-paper draft modeled on the ParsVoice structure, rewritten for Pashto.
- `docs/pashto_pipeline_plan.md` - implementation plan for building the corpus.
- `metadata/schema.md` - proposed release metadata schema.
- `notes/parsvoice_source_summary.md` - concise summary of the attached Persian paper.
- `tmp/pdfs/2510.10774v3.txt` - extracted text from the attached PDF for local reference.

## Working Name

`PashtoVoice` is used as a placeholder corpus name. Rename it before publication if you prefer a Pashto-language name.

## Immediate Next Steps

1. Choose permitted Pashto audio sources, especially audiobook, radio archive, educational, or public-domain long-form speech.
2. Select a baseline Pashto ASR model for transcription and boundary checks.
3. Build Pashto-specific text normalization for Arabic-script variants and Pashto-only letters.
4. Run a small pilot on 5-10 hours of audio before scaling.
5. Fill the `TBD` statistics in the paper draft from measured pipeline outputs.
