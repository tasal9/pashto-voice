# Pashto ASR Baseline Selection

## Selected Baseline: `uzair0/Katib-ASR`

Katib-ASR is selected as the first transcription and boundary-checking baseline for PashtoVoice.

Reasons:

- It is Pashto-specific rather than a generic multilingual ASR model.
- The model card reports a 28.23% WER on a held-out Pashto test set.
- It is based on Whisper large-v3 and fine-tuned on Common Voice Pashto 24, FLEURS Pashto, and an in-house curated Pashto corpus.
- The model card documents a Pashto normalization policy, including `ك` to `ک`, `ݢ`/`گ` to `ګ`, and Yey variants to `ی`.

## Operational Plan

Use Katib-ASR for:

- Transcribing long-form Pashto candidate segments.
- Re-transcription during boundary optimization.
- Pilot ASR quality checks.

Use independent ASR models for evaluation:

- Whisper large-v3 as a generic multilingual baseline.
- A smaller Pashto Whisper model where compute is limited.
- FLEURS/Common Voice references for WER/CER calculation.

## Compute Caveat

Katib-ASR is a large BF16 Whisper large-v3 model. GPU inference is strongly recommended. For CPU-only local smoke tests, run normalization and metadata stats first, then schedule ASR on a machine with a CUDA GPU.
