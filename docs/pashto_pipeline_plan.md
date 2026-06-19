# PashtoVoice Pipeline Plan

This plan adapts the ParsVoice pipeline to Pashto without assuming that Persian-specific tools transfer directly.

## 1. Data Collection

Prioritize sources that are legally releasable and useful for TTS:

- Public-domain or openly licensed Pashto audiobooks.
- Educational readings with clean narration.
- Radio archive speech only when licensing allows redistribution.
- Existing open datasets for comparison and ASR evaluation, especially Mozilla Common Voice Pashto.

Avoid mixing unreleasable sources into the public corpus. If a source can only be used for internal experimentation, keep it outside release metadata.

## 2. Audio Segmentation

Start with WebRTC VAD level 0, then compare against Silero VAD on a 5-10 hour pilot.

Target segment properties:

- Duration: 3-15 seconds preferred.
- Single speaker when possible.
- No music, overlap, clipping, or long silence.
- Sentence-level semantic completeness.

## 3. ASR Transcription

Evaluate at least three Pashto ASR options before choosing the production backend:

- Katib-ASR or another Pashto-fine-tuned Whisper model.
- Whisper large-v3 as a multilingual baseline.
- Any local or commercial ASR that supports Pashto, if licensing and privacy constraints allow it.

Report WER/CER on a held-out Pashto benchmark such as Common Voice or FLEURS where available.

## 4. Pashto Text Normalization

Normalize Arabic-script variants consistently:

- Arabic Kaf `ك` to Pashto/Persian Kaf `ک`.
- Arabic/Persian Gaf variants to Pashto `ګ` when appropriate.
- Yey variants to a chosen Pashto standard.
- Remove non-Pashto-script noise while preserving useful punctuation.

Track changes so the released corpus can include raw and normalized forms.

## 5. Sentence Completion Classifier

Train a binary classifier that predicts whether a transcript is a complete Pashto sentence.

Candidate model:

- XLM-R, mBERT, or a Pashto-specific encoder if a strong one is available.

Training data:

- Positive examples: complete Pashto sentences from curated text.
- Negative examples: sentences truncated by words and by final characters.
- Oversample incomplete examples to reflect VAD boundary failures.

## 6. Boundary Optimization

For each segment:

1. Save original ASR transcript.
2. Trim the start boundary with binary search up to a 3-second ceiling.
3. Re-transcribe after each candidate trim.
4. Accept the maximum trim that preserves the normalized transcript.
5. Repeat for the end boundary.
6. Fine-tune with 0.1-second steps.

If ASR instability prevents reliable comparison, mark the segment as unstable and exclude it from the TTS-ready subset.

## 7. Quality Scoring

Audio quality:

- Signal-to-noise ratio.
- Dynamic range.
- Clipping.
- Silence ratio.
- Background music.
- Duration range.

Pashto text quality:

- Valid Pashto character ratio.
- Segment length.
- Lexical repetition.
- Linguistic richness.
- Coverage of Pashto-specific letters and phoneme-bearing characters.

## 8. Speaker Identification

Use ECAPA-TDNN embeddings or a comparable speaker embedding model.

Pipeline:

1. Cluster speakers within each source recording.
2. Remove low-confidence segments.
3. Merge local clusters into global speaker IDs with cosine similarity thresholds.
4. Validate against known narrator metadata where available.

## 9. Punctuation Restoration

Train or adapt a Pashto punctuation restoration model after normalization. If no reliable model exists, release both unpunctuated and model-punctuated transcripts and mark punctuation confidence.

## 10. Evaluation

Fine-tune a multilingual TTS model such as XTTSv2, Parler-TTS, or another open multilingual model that can support Pashto text.

Evaluate:

- MOS for naturalness.
- SMOS for speaker similarity.
- Intelligibility MOS.
- WER/CER using ASR models independent of the transcription backend.
- Speaker embedding similarity with ECAPA-TDNN.

Use native Pashto raters and stratify reference speakers by dialect, gender, and age when metadata permits.
