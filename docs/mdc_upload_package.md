# Mozilla Data Collective Upload Package

This document combines the PashtoVoice speech corpus work and related Pashto text/OCR/NLP goals into a single MDC-facing dataset request. It is written for the MDC "Uploads" form field:

> Provide a short summary of your dataset, how the data was collected, and any additional links you'd like to share with the MDC team.

## Short Copy-Paste Version

PashtoVoice is a research dataset project for Pashto speech and language technology, focused on creating reusable data for ASR, TTS, speech-text alignment, punctuation restoration, text normalization, and future OCR/NLP evaluation. The current pilot contains a permission-approved long-form Pashto audio source from Amin Sultani's YouTube channel. We inventoried 73 candidate videos totaling about 18.56 hours, selected a first 25-video pilot totaling 8.301 raw hours, downloaded audio-only streams with permission, converted them to 16 kHz mono WAV, and segmented them into 2,317 candidate speech clips totaling 8.248 hours. Lightweight audio checks show strong quality: mean score 99.66/100, 2,288 high-quality segments, 29 acceptable segments, and no low-quality segments under the current scoring rules. We also maintain an 8-hour FLEURS Pashto metadata pilot for normalization and benchmarking, but the primary upload candidate is the permission-approved Amin Sultani long-form audio pilot. The project includes source-selection notes, permission tracking, metadata schemas, Pashto normalization utilities, segmentation scripts, audio-quality scoring, and planned Katib-ASR transcription. We will not include sources whose terms prohibit AI training or redistribution, such as Shariat Daily, unless explicit permission is obtained.

Project repository/package includes documentation and manifests for source provenance, conversion, segmentation, audio quality, and planned ASR/text-quality processing. Relevant project materials: `paper/pashtovoice_draft.md`, `docs/source_selection.md`, `metadata/schema.md`, `metadata/amin_sultani_segments_manifest.jsonl`, and `metadata/amin_sultani_audio_quality_summary.json`.

## Longer Version

PashtoVoice is a Pashto speech and language resource project modeled after modern low-resource speech corpus construction pipelines. The goal is to build a documented, reproducible, rights-aware Pashto corpus for text-to-speech, automatic speech recognition, speech-text alignment, punctuation restoration, Pashto text normalization, and future OCR/NLP evaluation.

The current upload candidate is the Amin Sultani long-form Pashto audio pilot. The channel was first inventoried metadata-only, without downloading media. After the project owner reported that permission was obtained, we selected 25 videos from the channel for a first long-form pilot. These videos total 8.301 raw hours. We downloaded the audio-only streams, converted them to 16 kHz mono WAV, and segmented the audio using ffmpeg silence detection. The resulting segment manifest contains 2,317 candidate clips totaling 8.248 hours, with a mean duration of 12.815 seconds and a median duration of 14.981 seconds.

Audio quality scoring is complete for the segmented pilot. The current lightweight scoring pass reports a mean audio quality score of 99.66/100, median 100.0/100, 2,288 high-quality segments, 29 acceptable segments, and zero low-quality segments. No clipping was detected. ASR transcription with Katib-ASR is the next processing stage, followed by Pashto text-quality scoring and manual review of a sample of predictions.

The project also includes a separate FLEURS Pashto metadata pilot used for benchmarking and text normalization validation. That pilot contains 2,265 segments, 8.0 hours, 58,868 tokens, and 7,692 unique word forms. FLEURS is not the main long-form upload candidate; it is maintained as a reference/benchmark source.

All sources are handled conservatively. The project tracks permission and source restrictions before release, while source-rights records are intentionally kept outside tracked public files. Sources with unclear or restrictive terms remain excluded from training/release manifests. For example, Shariat Daily is marked as not permitted for AI training because its `robots.txt` content signal includes `ai-train=no`, unless explicit written permission is later obtained.

## Current Dataset Numbers

| Item | Value |
| --- | ---: |
| Amin Sultani candidate inventory | 73 videos |
| Candidate inventory duration | 18.56 hours |
| Selected pilot videos | 25 |
| Raw selected pilot duration | 8.301 hours |
| Segmented pilot duration | 8.248 hours |
| Segmented clips | 2,317 |
| Mean segment duration | 12.815 seconds |
| Median segment duration | 14.981 seconds |
| Audio quality mean score | 99.66 / 100 |
| High-quality segments | 2,288 |
| Acceptable segments | 29 |
| Low-quality segments | 0 |

## Upload Caveats

- Public release should wait until source-rights records are verified outside tracked repository files.
- Katib-ASR transcription is pending.
- Text/transcript quality scoring is pending ASR output.
- Final TTS-ready subset statistics are pending ASR review and filtering.
- Shariat Daily and other text sources should not be included unless explicit permission is obtained.
