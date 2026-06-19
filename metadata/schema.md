# PashtoVoice Metadata Schema

This schema is designed for both an ASR-oriented processed subset and a stricter TTS-ready subset.

## Segment-Level Fields

| Field | Type | Description |
| --- | --- | --- |
| `segment_id` | string | Stable unique segment identifier. |
| `source_id` | string | Original book, program, archive item, or recording identifier. |
| `audio_path` | string | Relative path to the released audio segment. |
| `start_time_sec` | float | Segment start time in the source audio. |
| `end_time_sec` | float | Segment end time in the source audio. |
| `duration_sec` | float | Segment duration after boundary optimization. |
| `transcript_raw` | string | ASR or source transcript before normalization. |
| `transcript_normalized` | string | Pashto-normalized transcript. |
| `transcript_punctuated` | string | Final punctuation-restored transcript. |
| `speaker_id` | string | Automatically inferred global speaker ID. |
| `speaker_confidence` | float | Speaker-clustering confidence in `[0, 1]`. |
| `source_speaker_name` | string | Metadata speaker/narrator name when available. |
| `dialect` | string | Known dialect label when available; otherwise `unknown`. |
| `gender` | string | Metadata or self-reported gender when available; otherwise `unknown`. |
| `text_quality_score` | float | Pashto text-quality score in `[0, 1]`. |
| `audio_quality_score` | float | Audio-quality score in `[0, 100]`. |
| `sentence_complete` | bool | Sentence-completion classifier output. |
| `contains_music` | bool | Background music detector output. |
| `split` | string | Suggested split: `train`, `dev`, `test`, or `unassigned`. |
| `license` | string | License for the source audio and transcript. |

## Source-Level Fields

| Field | Type | Description |
| --- | --- | --- |
| `source_id` | string | Stable source identifier. |
| `title` | string | Book/program/title when known. |
| `source_url` | string | Original URL when available. |
| `source_type` | string | `audiobook`, `radio`, `educational`, `public_speech`, etc. |
| `license` | string | License or reuse status. |
| `recording_quality` | string | Source-level quality note. |
| `known_speakers` | string | Human-readable speaker/narrator metadata. |
| `region` | string | Region/country when known. |
| `notes` | string | Manual notes and provenance caveats. |
