# PashtoVoice Common Voice-Style Corpus

A Pashto speech-text corpus packaged in a Mozilla Common Voice-compatible format.

## Release Snapshot

| Split | Clips |
| --- | --- |
| validated | 2288 |
| other (needs review) | 29 |
| invalidated | 0 |
| **Total** | **2317** |

## Quick Start

Each TSV file is UTF-8 encoded and tab-separated with a header row.
Audio clips live under `clips/` and are referenced by the `path` column.

```python
import pandas as pd
validated = pd.read_csv("validated.tsv", sep="	")
```

## Fields

See `docs/common_voice_format.md` in the source repository for the full schema and validation rules.

## Source

Primary source: `Amin Sultani YouTube Pilot`
Locale: `ps`

## Notes and Known Limitations

- Manual Common Voice up/down votes are not yet collected. Validation status is derived from automated audio quality scores.
- Transcripts are populated from ASR outputs when available. Segments without ASR output have empty `sentence` fields and require transcription.
- Please review licensing and permission records before redistributing derived audio or text.

## Citation

See `CITATION.bib`.
