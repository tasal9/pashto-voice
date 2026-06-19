# ParsVoice Source Paper Summary

Source PDF: `/Users/yaqoobtasal/Downloads/2510.10774v3.pdf`

Title: "ParsVoice: A Large-Scale Multi-Speaker Persian Speech Corpus for Text-to-Speech Synthesis"

Authors: Mohammad Javad Ranjbar Kalahroodi, Heshaam Faili, Azadeh Shakery

## Main Contribution

The paper introduces ParsVoice, a large Persian speech-text corpus designed for multi-speaker TTS. It also presents an automated pipeline for turning long-form audiobook recordings into sentence-level aligned speech-text data.

## Key Reported Numbers

- Source: IranSeda audiobooks.
- Processed ASR-oriented subset: 4,096.2 hours, 2,999,296 segments.
- Final TTS subset: 2,199.7 hours, 1,364,671 segments.
- Speaker IDs: 1,815 automatically identified global speakers.
- Validation model: XTTSv2 fine-tuned for Persian.
- Subjective results: MOS about 3.6/5, SMOS about 4.0/5.

## Pipeline Shape

1. Collect long-form audiobooks.
2. Segment audio with VAD.
3. Transcribe candidate segments with ASR.
4. Detect whether each transcript is a complete sentence.
5. Extend incomplete segments iteratively.
6. Optimize segment boundaries by trimming while preserving ASR text.
7. Score audio quality and language-specific text quality.
8. Cluster speaker embeddings into local and global speaker IDs.
9. Restore punctuation.
10. Release final audio, transcripts, speaker IDs, and quality metadata.

## Pashto Adaptation Notes

The structure transfers well to Pashto, but the language-specific pieces must change:

- Replace ParsBERT with a Pashto-capable model, or fine-tune a multilingual model such as XLM-R for sentence-completion detection.
- Replace Persian normalization with Pashto script normalization, including Arabic/Persian/Pashto letter variants.
- Add explicit checks for Pashto-only letters such as ټ, ډ, ړ, ږ, ڼ, ګ, ښ, څ, ځ, and څ/ځ/ږ/ښ confusions.
- Choose a Pashto ASR backend carefully; Pashto ASR remains weaker than Persian ASR.
- Treat dialect coverage as a central corpus property, especially Afghan and Pakistani Pashto varieties.
