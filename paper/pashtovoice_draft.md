# PashtoVoice: A Large-Scale Multi-Speaker Pashto Speech Corpus for Text-to-Speech Synthesis

Author names: TBD

Affiliations: TBD

## Abstract

Pashto remains underrepresented in open speech-text resources despite being spoken by tens of millions of people across Afghanistan, Pakistan, and the diaspora. Recent growth in community speech resources has improved Pashto ASR research, but high-quality, sentence-aligned, multi-speaker data suitable for text-to-speech (TTS) remains limited. We introduce PashtoVoice, a planned large-scale Pashto speech-text corpus and construction pipeline for building TTS-ready data from long-form Pashto recordings. The pipeline combines voice activity detection, Pashto ASR transcription, sentence-completion classification, ASR-stable boundary optimization, Pashto-specific text normalization, speaker identification, punctuation restoration, and audio-text quality filtering. The released corpus will include aligned audio segments, normalized and punctuated transcripts, inferred speaker IDs, source metadata, and quality scores. To validate the corpus, we will fine-tune a multilingual TTS model on the final TTS subset and evaluate naturalness, speaker similarity, and intelligibility with native Pashto raters and independent ASR systems.

## 1. Introduction

The rapid progress of generative speech models has increased the need for large, clean, and linguistically diverse speech corpora. For many high-resource languages, researchers can rely on hundreds or thousands of hours of aligned speech-text data. Pashto, by contrast, has historically had very limited open speech resources, especially for TTS.

Pashto presents challenges that make direct transfer from related languages unreliable. It is written in an extended Arabic script, contains Pashto-specific letters that are often omitted or substituted in informal digital text, and spans major dialectal varieties across Afghanistan and Pakistan. These properties affect ASR, normalization, sentence segmentation, grapheme-to-phoneme behavior, and TTS pronunciation.

Recent Mozilla Common Voice work has substantially changed the Pashto speech-data landscape. The Mozilla Data Collective datasheet for Common Voice Pashto 26.0 reports 5,193,154 clips, 5,521.62 recorded hours, 3,261 validated hours, and 8,355 speakers. However, Common Voice is primarily an ASR-oriented read-speech corpus, and its current datasheet forbids speaker-identification attempts and re-hosting. TTS training benefits from stricter constraints: clean audio, complete sentences, accurate punctuation, stable speaker labels where legally allowed, minimal background noise, and reliable sentence-level alignment.

PashtoVoice targets this gap by adapting a ParsVoice-style audiobook-to-corpus pipeline to Pashto. The goal is not only to release a corpus, but also to provide a reproducible method for constructing high-quality Pashto speech-text data when reference transcripts are missing, incomplete, or not aligned to the exact audio edition.

## 2. Related Work

### 2.1 Speech Corpora for High-Resource Languages

High-resource TTS and ASR research has benefited from datasets such as LibriSpeech, LJSpeech, VCTK, Common Voice, Multilingual LibriSpeech, and VoxPopuli. These resources provide useful baselines for scale, speaker diversity, and documentation practices, but their coverage remains uneven across languages.

### 2.2 Pashto Speech Datasets

Pashto speech resources have expanded recently but remain uneven for TTS. The Pashto Common Voice corpus is the most visible open community dataset and has become important for ASR research. Common Voice Pashto 26.0 reports 5,521.62 total recorded hours and 3,261 validated hours, while earlier analyses documented rapid growth across releases. Because Common Voice forbids speaker-identification attempts, it is best treated as an ASR benchmark or non-rehosted training source rather than the main speaker-clustered PashtoVoice release.

Other resources include PashtoCoST/PLDST, a controlled speech-text dataset with 20,000 recordings from five native speakers, together with Pashto text, English translation, and romanized transcription. Commercial Pashto ASR datasets also exist, but access restrictions limit reproducibility and public benchmarking.

### 2.3 Pashto TTS Systems

Public Pashto TTS systems and datasets remain less mature than ASR resources. Many deployed Pashto TTS services are closed, and open multi-speaker TTS-ready corpora with high-quality aligned transcripts, speaker labels, and release metadata are scarce. PashtoVoice is designed to support raw-text Pashto TTS research while also enabling experiments with optional phoneme or romanization features.

## 3. PashtoVoice

PashtoVoice is a pipeline for converting long-form Pashto recordings into a structured, high-quality speech-text corpus. The pipeline is designed for sources where exact transcripts may be unavailable, unreliable, or mismatched to the audio.

### 3.1 Data Collection and Source Selection

Candidate sources include Pashto audiobooks, educational readings, public speeches, and radio-style narrative recordings when redistribution rights permit release. We prioritize recordings with clean narration, stable speakers, minimal background music, and clear licensing. For the first technical pilot, we selected FLEURS Pashto because it is CC-BY-4.0, benchmark-like, and large enough for a 5-10 hour smoke test. For the first true long-form pilot, Books for Afghanistan and Darakht-e Danesh are the strongest audiobook-style candidates, but both require explicit permission before redistributed derivative segments can be released.

Unlike community prompt-read corpora, long-form sources provide extended prosodic context and richer lexical coverage. However, they also require careful segmentation and alignment. When source transcripts are not available, transcription is produced by ASR and then filtered through quality checks.

### 3.2 Intelligent Audio Segmentation

Raw recordings are first segmented using VAD. A pilot comparison will evaluate WebRTC VAD, Silero VAD, and Whisper-based segmentation. Candidate segments are transcribed by Katib-ASR, our selected Pashto baseline, and checked for sentence completeness.

For incomplete segments, the boundary is extended in small increments and the segment is re-transcribed. The loop continues until the sentence-completion classifier predicts a complete sentence or the maximum extension limit is reached. Remaining incomplete items are retained in the processed subset with an incompleteness flag, but excluded from the strict TTS-ready subset.

### 3.3 Pashto Sentence-Completion Classifier

The sentence-completion classifier predicts whether a transcript forms a complete Pashto sentence. We will fine-tune a Pashto-capable encoder such as XLM-R, mBERT, or a dedicated Pashto language model. The first implementation also includes deterministic Pashto normalization for Arabic Kaf, Gaf variants, Yey variants, diacritics, tatweel, zero-width joiners, and non-Arabic-script noise.

Training examples will be generated from curated Pashto text. Complete sentences serve as positives. Negative examples are created by truncating final words or removing final characters, matching the common failure mode where VAD cuts off the end of a sentence.

### 3.4 Boundary Optimization

Each candidate segment is optimized at the start and end boundaries. The system trims a candidate amount of audio, re-runs ASR, normalizes both transcripts, and compares them. If the transcript changes, the trim is considered too aggressive. Binary search finds the maximum stable trim, followed by 0.1-second linear refinement.

This ASR-stability criterion avoids relying on word-level timestamps, which may be unavailable or unreliable for Pashto. Segments with unstable ASR outputs during boundary search are excluded from the TTS-ready subset.

### 3.5 Pashto Text and Audio Quality Assessment

Text quality scoring combines:

- Valid Pashto character ratio.
- Length quality.
- Repetition and lexical diversity.
- Dialect/script normalization consistency.
- Coverage of Pashto-specific letters and phoneme-bearing characters.

Audio quality scoring combines:

- Signal-to-noise ratio.
- Dynamic range.
- Clipping ratio.
- Silence ratio.
- Background music detection.
- Duration range.

Quality thresholds will be calibrated by manual review on a pilot subset before large-scale processing.

### 3.6 Speaker Identification

Speaker identification uses speaker embeddings to assign consistent speaker IDs. Local clustering is performed within each long-form source, then local speaker centroids are merged into global speaker identities. Low-confidence segments and very small clusters are excluded from the TTS-ready subset.

Where narrator names or speaker metadata are available, they are used only for validation and documentation, not as the sole source of speaker identity.

### 3.7 Punctuation Restoration and Final Preparation

ASR transcripts are normalized and then passed through a Pashto punctuation restoration model. If punctuation restoration confidence is low, both unpunctuated and punctuated transcripts will be released.

The final TTS-ready subset excludes segments with low audio quality, low text quality, background music, incomplete sentences, unstable boundary optimization, or low-confidence speaker labels.

### 3.8 Dataset Release

PashtoVoice will release audio segments, normalized transcripts, punctuation-restored transcripts, speaker IDs, quality scores, source identifiers, and split assignments. The broader processed subset can support ASR and alignment research, while the stricter subset targets TTS training.

## 4. Corpus Analysis

This section will be filled after processing. The first attempted FLEURS Pashto pilot was blocked by remote dataset transfer in the local environment before any rows were produced, so no corpus statistics are reported here yet. Planned statistics include:

| Metric | Processed ASR-Oriented Subset | Final TTS Subset |
| --- | ---: | ---: |
| Total hours | pending pilot transfer | pending long-form source clearance |
| Segments | pending pilot transfer | pending long-form source clearance |
| Speakers | not used for FLEURS/Common Voice pilot | pending permitted source |
| Total tokens | pending pilot transfer | pending long-form source clearance |
| Unique word forms | pending pilot transfer | pending long-form source clearance |
| Mean segment duration | pending pilot transfer | pending long-form source clearance |
| Median segment duration | pending pilot transfer | pending long-form source clearance |

We will also report source distribution, dialect metadata where available, gender metadata where available, quality-score distributions, boundary-trimming statistics, and speaker-clustering purity against known metadata.

## 5. Evaluation: TTS Model Training

To validate the corpus, we will fine-tune a multilingual TTS model capable of Pashto synthesis. Candidate models include XTTSv2 and other open multilingual TTS systems.

### 5.1 Model Adaptation

The selected model will be adapted to Pashto text. Depending on the model, this may require tokenizer extension, Pashto text normalization, or optional phoneme/romanization support. Training details will report GPU hardware, batch size, optimizer, learning rate, number of steps, and held-out validation configuration.

### 5.2 Subjective Evaluation

Native Pashto raters will evaluate generated samples for:

- Naturalness MOS.
- Speaker similarity MOS.
- Intelligibility MOS.

Reference speakers should be external to the training set when possible, with balanced sampling across gender, age, and dialect metadata.

### 5.3 Objective Evaluation

Objective intelligibility will be measured using WER and CER from ASR systems that are independent of the transcription backend. Speaker similarity will be measured using speaker embedding cosine similarity between reference and generated speech.

## 6. Conclusion

PashtoVoice aims to address the shortage of high-quality Pashto TTS data by combining large-scale speech collection with sentence-aware segmentation, ASR-stable boundary optimization, Pashto-specific text processing, speaker identification, and quality filtering. The resulting corpus and pipeline are intended to support reproducible Pashto TTS, ASR, alignment, punctuation restoration, and low-resource speech-language research.

## 7. Limitations

Several limitations should be expected. First, long-form read speech may not represent conversational Pashto. Second, ASR transcription errors may remain even after filtering. Third, speaker IDs inferred by clustering are not manually verified identities. Fourth, dialect and demographic metadata may be incomplete. Fifth, licensing constraints may limit which sources can be publicly released.

## Appendix A. VAD Comparison Plan

Evaluate VAD methods on a pilot subset and report completion rate, average segment duration, and manual quality judgments.

| VAD Method | Completion Rate | Notes |
| --- | ---: | --- |
| WebRTC level 0 | TBD | Pilot baseline |
| WebRTC level 1 | TBD | TBD |
| Silero VAD | TBD | TBD |
| Whisper-based segmentation | TBD | TBD |

## Appendix B. ASR Comparison Plan

Evaluate ASR systems on held-out Pashto speech with normalized references.

| ASR System | WER | CER | Notes |
| --- | ---: | ---: | --- |
| Katib-ASR | 28.23 reported on model-card held-out set | TBD on PashtoVoice pilot | Selected production baseline |
| Whisper large-v3 | TBD | TBD | Multilingual baseline |
| Other Pashto ASR | TBD | TBD | Optional |

## Appendix C. Text Quality Scoring Draft

| Dimension | Weight | Description |
| --- | ---: | --- |
| Character quality | 0.25 | Valid Pashto characters and digits; penalizes script substitutions and noise. |
| Length quality | 0.20 | Rewards useful sentence lengths for TTS. |
| Repetition score | 0.20 | Penalizes repeated words and degenerate ASR output. |
| Linguistic complexity | 0.175 | Measures common-word balance and word-length distribution. |
| Pashto letter coverage | 0.175 | Rewards coverage of Pashto-specific letters and phoneme-bearing characters. |

## References

- ParsVoice source paper: Mohammad Javad Ranjbar Kalahroodi, Heshaam Faili, Azadeh Shakery. "ParsVoice: A Large-Scale Multi-Speaker Persian Speech Corpus for Text-to-Speech Synthesis." arXiv:2510.10774v3.
- PashtoCoST/PLDST dataset: https://data.mendeley.com/datasets/8f8fhpdxcc/3
- Pashto Common Voice release-level analysis: https://arxiv.org/html/2602.14062v1
- Pashto Common Voice corpus paper: https://arxiv.org/html/2603.27021v1
- Katib-ASR model card: https://huggingface.co/uzair0/Katib-ASR
