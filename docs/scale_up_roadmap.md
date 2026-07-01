# PashtoVoice Scale-Up Roadmap

This roadmap turns the current 8-hour long-form pilot into a larger Pashto speech corpus while keeping source rights, quality gates, and reproducibility visible.

## Current Baseline

- Amin Sultani long-form pilot: 25 videos, 2,317 segments, 8.248 segmented hours.
- Audio quality is strong: mean score 99.66, no clipping, 2,288 segments at score 90 or higher.
- Katib-ASR is locally loadable and a 10-row CPU pilot completed. Full ASR remains the main blocker before scaling because CPU inference is slow.
- Text-quality pilot: 10 ASR rows scored, mean score 0.7422, 3 high-quality rows, 7 review rows, 0 low-quality rows.

## Expansion Targets

| Stage | Target | Purpose | Exit Criteria |
| --- | ---: | --- | --- |
| Pilot ASR | 1-2 hours | Confirm Katib-ASR setup and output schema | Resumable ASR output, manual review sample, rough WER/CER where references exist |
| Full Source Pilot | 8 hours | Finish current Amin Sultani subset | ASR complete, text quality report, exclusion rules documented |
| Channel Expansion | 18 hours | Process all permission-covered Amin Sultani candidates | Source manifest, segment manifest, ASR manifest, quality summary |
| Multi-Source Release Candidate | 50-100 hours | Add additional cleared sources | Permission record per source, speaker/source balance report, train/dev/test split |
| Large Corpus | 300+ hours | Broader Pashto ASR/TTS research corpus | Reproducible pipeline, dataset card, known limitations, benchmark results |

## Near-Term Workstream

1. Finish Katib-ASR transcription for `metadata/amin_sultani_segments_manifest.jsonl`.
2. Run text-quality scoring and manual review on ASR outputs.
3. Use Common Voice and FLEURS for ASR benchmarking and normalization checks.
4. Keep source-rights records outside tracked files and verify redistribution scope before public release.
5. Request or confirm additional permissions from Books for Afghanistan and Darakht-e Danesh.
6. Scale from the 25-video pilot to all permission-covered Amin Sultani videos.

## Source Expansion Rules

- Do not process a new source for public release until permission and underlying text/audio rights are recorded.
- Keep unreleasable or uncertain sources outside release manifests.
- Track every generated manifest back to a source-level metadata record.
- Run the same segmentation, ASR, and quality scripts for every source so statistics remain comparable.

## Recommended Commands

Predownload Katib-ASR model files:

```bash
HF_HUB_DISABLE_XET=1 .venv/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('uzair0/Katib-ASR', allow_patterns=['config.json','generation_config.json','model.safetensors','processor_config.json','tokenizer.json','tokenizer_config.json'], resume_download=True)"
```

Smoke-test ASR:

```bash
.venv/bin/python scripts/run_katib_asr.py metadata/amin_sultani_segments_manifest.jsonl --limit 25 --device cpu --out metadata/katib_asr_smoke.jsonl --continue-on-error
```

Full resumable ASR run:

```bash
.venv/bin/python scripts/run_katib_asr.py metadata/amin_sultani_segments_manifest.jsonl --resume --out metadata/amin_sultani_katib_asr.jsonl --continue-on-error --progress-every 25
```

If CUDA is available, replace `--device cpu` with `--device cuda`.

On CPU, schedule the full run as a long/overnight job. The first 10 pilot rows took about 10.2 minutes.

Text quality scoring after ASR:

```bash
.venv/bin/python scripts/text_quality_stats.py metadata/amin_sultani_katib_asr.jsonl --out metadata/amin_sultani_text_quality.jsonl --summary-out metadata/amin_sultani_text_quality_summary.json
```

Manual review export after text-quality scoring:

```bash
.venv/bin/python scripts/export_manual_review.py metadata/amin_sultani_text_quality.jsonl --out metadata/amin_sultani_manual_review.csv --limit 100
```

## Metrics To Track As The Corpus Grows

- Total segmented hours and release-ready hours.
- Source count and hours per source.
- Speaker count when permitted by source terms.
- Duration distribution: below 3 seconds, 3-15 seconds, 15-18 seconds, above target.
- Audio quality buckets: high, acceptable, low.
- Text quality buckets after ASR.
- Train/dev/test split hours and source leakage checks.
