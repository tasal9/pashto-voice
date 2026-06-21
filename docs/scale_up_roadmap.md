# PashtoVoice Scale-Up Roadmap

This roadmap turns the current 8-hour long-form pilot into a larger Pashto speech corpus while keeping source rights, quality gates, and reproducibility visible.

## Current Baseline

- Amin Sultani long-form pilot: 25 videos, 2,317 segments, 8.248 segmented hours.
- Audio quality is strong: mean score 99.66, no clipping, 2,288 segments at score 90 or higher.
- Main blocker before scaling: ASR transcription and transcript quality scoring.

## Expansion Targets

| Stage | Target | Purpose | Exit Criteria |
| --- | ---: | --- | --- |
| Pilot ASR | 1-2 hours | Confirm Katib-ASR setup and output schema | Resumable ASR output, manual review sample, rough WER/CER where references exist |
| Full Source Pilot | 8 hours | Finish current Amin Sultani subset | ASR complete, text quality report, exclusion rules documented |
| Channel Expansion | 18 hours | Process all permission-covered Amin Sultani candidates | Source manifest, segment manifest, ASR manifest, quality summary |
| Multi-Source Release Candidate | 50-100 hours | Add additional cleared sources | Permission record per source, speaker/source balance report, train/dev/test split |
| Large Corpus | 300+ hours | Broader Pashto ASR/TTS research corpus | Reproducible pipeline, dataset card, known limitations, benchmark results |

## Near-Term Workstream

1. Run a Katib-ASR smoke test on 25-50 segments.
2. Manually inspect predictions for script normalization issues and obvious hallucinations.
3. Run resumable ASR on the full `metadata/amin_sultani_segments_manifest.jsonl` file.
4. Add text quality scoring over ASR predictions: Pashto character ratio, token count, repetition, empty prediction, and length mismatch.
5. Merge audio and text quality into a release-candidate segment manifest.
6. Expand from the selected 25-video pilot to all permission-covered Amin Sultani videos.

## Source Expansion Rules

- Do not process a new source for public release until permission and underlying text/audio rights are recorded.
- Keep unreleasable or uncertain sources outside release manifests.
- Track every generated manifest back to a source-level metadata record.
- Run the same segmentation, ASR, and quality scripts for every source so statistics remain comparable.

## Recommended Commands

Smoke-test ASR:

```bash
python scripts/run_katib_asr.py metadata/amin_sultani_segments_manifest.jsonl --limit 25 --device cpu --out metadata/katib_asr_smoke.jsonl --continue-on-error
```

Full resumable ASR run:

```bash
python scripts/run_katib_asr.py metadata/amin_sultani_segments_manifest.jsonl --resume --out metadata/amin_sultani_katib_asr.jsonl --continue-on-error --progress-every 25
```

If CUDA is available, replace `--device cpu` with `--device cuda`.

## Metrics To Track As The Corpus Grows

- Total segmented hours and release-ready hours.
- Source count and hours per source.
- Speaker count when permitted by source terms.
- Duration distribution: below 3 seconds, 3-15 seconds, 15-18 seconds, above target.
- Audio quality buckets: high, acceptable, low.
- Text quality buckets after ASR.
- Train/dev/test split hours and source leakage checks.