# PashtoVoice Common Voice-Style Corpus Format

This document defines the Mozilla Common Voice-compatible release format used by PashtoVoice.

## Directory Layout

```
pashtovoice_commonvoice/
├── clips/                          # Audio clip files
│   ├── <audio_id>/
│   │   └── <clip_filename>.wav
├── validated.tsv                   # High-quality clips (audio_quality_score >= 90)
├── other.tsv                       # Acceptable clips needing review (75 <= score < 90)
├── invalidated.tsv                 # Low-quality or invalid clips (score < 75)
├── reported.tsv                    # User-reported clips (empty until reported)
├── README.md                       # Corpus documentation
├── LICENSE.md                      # License summary
└── CITATION.bib                    # Citation entry
```

## TSV Schema

Each manifest TSV uses UTF-8 encoding, tab-separated values, and a header row.

| Column | Type | Description |
| --- | --- | --- |
| `path` | string | Relative path to the clip under `clips/`. |
| `sentence` | string | Transcript sentence (raw). Empty if ASR is pending. |
| `sentence_normalized` | string | Pashto-normalized transcript (no diacritics, unified letters). Empty if ASR is pending. |
| `up_votes` | int | Common Voice validation up-votes (0 until manually validated). |
| `down_votes` | int | Common Voice validation down-votes (0 until manually validated). |
| `age` | string | Speaker age bucket when known; otherwise empty. |
| `gender` | string | Speaker gender when known; otherwise empty. |
| `accent` | string | Dialect/accent label when known; otherwise empty. |
| `locale` | string | BCP-47 locale (`ps` for Pashto). |
| `segment_id` | string | Stable PashtoVoice segment identifier. |
| `source_id` | string | Source identifier (e.g., `youtube_amin_sultani`). |
| `audio_id` | string | Parent audio/recording identifier. |
| `start_time_sec` | float | Start time in the parent audio. |
| `end_time_sec` | float | End time in the parent audio. |
| `duration_sec` | float | Clip duration in seconds. |
| `audio_quality_score` | float | Audio quality score in `[0, 100]`. |
| `text_quality_score` | float | Text quality score in `[0, 1]` when transcript exists. |
| `speaker_id` | string | Inferred or metadata speaker ID when known. |
| `split` | string | Suggested split: `train`, `dev`, `test`, or empty. |

## Validation Rules

- Every `path` must resolve to an existing file under `clips/`.
- `duration_sec` must be positive and match the actual audio duration when audio is present.
- `sentence` and `sentence_normalized` may be empty when ASR/manual transcription is pending (including for clips that land in `validated.tsv` via audio-quality scoring).
- All rows must use locale `ps`.

## Source-to-Common-Voice Mappings

| PashtoVoice field | Common Voice / release field |
| --- | --- |
| `segment_id` | `segment_id` |
| `audio_path` | `path` (rebased to `clips/`) |
| `transcript` / `prediction` / `reference` | `sentence` |
| `transcript_normalized` / `prediction_normalized` | `sentence_normalized` |
| `duration_sec` | `duration_sec` |
| `start_time_sec` | `start_time_sec` |
| `end_time_sec` | `end_time_sec` |
| `source_id` | `source_id` |
| `audio_id` | `audio_id` |
| `speaker_id` | `speaker_id` |
| `gender` | `gender` |
| `dialect` | `accent` |
| `audio_quality_score` | `audio_quality_score` |
| `text_quality_score` | `text_quality_score` |
| `split` | `split` |

## Quality-Based Validation Proxy

Because manual Common Voice votes are not yet collected, validation status is derived from the automated audio quality score:

- `validated.tsv`: `audio_quality_score >= 90`
- `other.tsv`: `75 <= audio_quality_score < 90`
- `invalidated.tsv`: `audio_quality_score < 75`
