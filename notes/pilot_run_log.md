# Pilot Run Log

Date: 2026-06-20

## Goal

Run a 5-10 hour Pashto pilot before scaling.

## Selected Pilot Source

FLEURS Pashto (`google/fleurs`, config `ps_af`) was selected for the first technical pilot because it is release-safe for research use under CC-BY-4.0 and has enough Pashto speech for a 5-10 hour smoke test.

## Status

Blocked by remote dataset transfer in the current local environment.

Two attempts were made:

1. Standard `datasets.load_dataset("google/fleurs", "ps_af")`.
2. Streaming mode with `HF_HUB_DISABLE_XET=1`.

Both attempts stalled before producing the first row. The stuck Python download processes were terminated cleanly.

## Verified Locally

- Python dependencies installed: `datasets`, `soundfile`, `jiwer`.
- FLEURS Pashto config name confirmed: `ps_af`.
- Pashto normalizer executed successfully.
- Pilot/stat scripts compile successfully.
- Stats pipeline verified with `metadata/sample_manifest.jsonl`.

## Next Action

Retry the pilot on a network path where Hugging Face dataset shards download normally, or manually download the FLEURS Pashto parquet/audio files and point the manifest builder at local files.
