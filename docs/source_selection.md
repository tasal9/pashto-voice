# PashtoVoice Source Selection

This list separates sources that are immediately usable for measurement from sources that are promising but require permission or extra legal review before inclusion in a redistributed corpus.

## Selected Pilot Source

### FLEURS Pashto

- Use: 5-10 hour pilot, ASR evaluation, normalization smoke tests.
- Status: permitted for research use with attribution.
- License: CC-BY-4.0.
- Strengths: clean read speech, transcripts, stable benchmark structure, simple reproducibility.
- Limitations: not long-form and not audiobook-style, so it should not be treated as the final PashtoVoice source domain.
- Decision: use for the first local pilot because it is accessible and release-safe for derived statistics.

## Primary Release Candidate

### Mozilla Common Voice Pashto 26.0

- Use: ASR baseline evaluation, normalization testing, possible TTS subset under Mozilla access rules.
- License: CC0-1.0.
- Current size: 5,193,154 clips, 5,521.62 recorded hours, 3,261 validated hours, 8,355 speakers.
- Important constraints: the Mozilla Data Collective page forbids attempting to identify speakers and forbids re-hosting or re-sharing the dataset.
- Decision: use as a benchmark and optional non-rehosted training source. Do not run speaker identification on Common Voice clips.

## Long-Form Candidates Requiring Clearance

### Amin Sultani YouTube Channel

- URL: https://www.youtube.com/@AminSultani10/videos
- Use: audiobook/podcast-style Pashto long-form speech.
- Evidence: public search results describe the channel as hosting audiobooks, podcasts, information, and entertainment videos. A metadata-only `yt-dlp --flat-playlist --skip-download` inventory found 73 videos with duration metadata, totaling approximately 18.56 candidate hours.
- Status: permission-gated source approved for the local pilot. Permission records are intentionally not tracked in the public repository.
- Risks: some videos appear to be readings or translations of copyrighted books, so permission may need to cover both the narrator/channel audio and the underlying text/book rights.
- Decision: selected as the first true long-form Pashto pilot source. If permission does not cover underlying book/text rights, keep affected titles internal or exclude them from public redistribution.

### Books for Afghanistan / Hoopoe Audio

- Use: children storybook audio; useful for clean narrative Pashto.
- Evidence: the site lists downloadable Pashto MP3 audio for multiple titles.
- Status: permission required before redistributing derived audio segments or transcripts.
- Decision: promising for a long-form/narrative pilot after direct permission.

### Darakht-e Danesh Library Pashto Audiobooks

- Use: educational audiobook-style Pashto.
- Evidence: the library announces free Pashto audiobooks.
- Status: the page says content is free in the DD Library, but the page footer says all rights reserved. Treat as listen-only until permission is obtained.
- Decision: contact DDL for explicit corpus-building and redistribution permission.

### Global Recordings Network Pashto Programs

- Use: scripted long-form religious narrative/audio lessons with downloadable MP3 and scripts.
- Status: downloadable, but page-level terms allow personal/local ministry copying only when unmodified and not sold/bundled. This is not sufficient for a public ML corpus.
- Decision: not selected for public corpus unless GRN grants additional permission.

### Internet Archive Pashto Public-Domain Items

- Use: public-domain text and possible audio where item-level audio exists.
- Status: item-by-item review required. Many Pashto records are text scans, music, or non-speech, and item metadata may be unreliable.
- Decision: use only items with clear public-domain or compatible Creative Commons audio, not just scanned texts.

## Recommended Order

1. Finish Katib-ASR transcription for the Amin Sultani segments.
2. Run text-quality scoring and manual review on ASR outputs.
3. Use Common Voice and FLEURS for ASR benchmarking and normalization checks.
4. Keep source-rights records outside tracked files and verify redistribution scope before public release.
5. Request or confirm additional permissions from Books for Afghanistan and Darakht-e Danesh.
6. Scale from the 25-video pilot to all permission-covered Amin Sultani videos.
