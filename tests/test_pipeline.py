import sys
import unittest
import math
import wave
import tempfile
import json
from pathlib import Path

# Add scripts directory to sys.path so we can import the modules
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.append(str(scripts_dir))

import pashto_normalize
import audio_quality_stats
import pilot_stats
import text_quality_stats
import export_manual_review
import export_common_voice
import validate_common_voice


class TestPashtoNormalize(unittest.TestCase):
    def test_normalization_kaf(self):
        # Arabic Kaf should map to Pashto/Persian Kaf
        self.assertEqual(pashto_normalize.normalize_pashto("كتاب"), "کتاب")

    def test_normalization_gaf(self):
        # Persian Gaf should map to Pashto Gaf
        self.assertEqual(pashto_normalize.normalize_pashto("ګتفګو"), "ګتفګو")
        self.assertEqual(pashto_normalize.normalize_pashto("گتفګو"), "ګتفګو")

    def test_normalization_yeh(self):
        # Arabic Yeh and other variants should map to Pashto Yeh
        self.assertEqual(pashto_normalize.normalize_pashto("يکشنبه"), "یکشنبه")
        self.assertEqual(pashto_normalize.normalize_pashto("ىکشنبه"), "یکشنبه")

    def test_remove_punctuation(self):
        self.assertEqual(
            pashto_normalize.normalize_pashto("کتاب، قلم؟", remove_punctuation=True),
            "کتاب قلم"
        )
        self.assertEqual(
            pashto_normalize.normalize_pashto("کتاب، قلم؟", remove_punctuation=False),
            "کتاب، قلم؟"
        )

    def test_character_ratio(self):
        # 100% Pashto characters
        self.assertAlmostEqual(pashto_normalize.pashto_character_ratio("کتاب قلم"), 1.0)
        # 0% Pashto characters
        self.assertAlmostEqual(pashto_normalize.pashto_character_ratio("hello world"), 0.0)

    def test_specific_coverage(self):
        # String with unique Pashto-specific letters: پ, ټ, ډ, ړ, ږ, ښ, څ, ځ, ڼ, ګ, ۍ, ې
        text_with_specific = "پټډړ"
        coverage = pashto_normalize.pashto_specific_coverage(text_with_specific)
        self.assertGreater(coverage, 0.0)


class TestAudioQualityStats(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_dummy_wav(self, filename: str, amplitude: int = 10000, duration_sec: float = 1.0, clip: bool = False) -> Path:
        wav_path = self.temp_path / filename
        sample_rate = 16000
        num_samples = int(sample_rate * duration_sec)
        
        with wave.open(str(wav_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit PCM
            wf.setframerate(sample_rate)
            
            # Write a simple sine-wave or constant PCM data
            frames = []
            for i in range(num_samples):
                val = int(amplitude * math.sin(2 * math.pi * 440 * i / sample_rate))
                if clip:
                    # Clip signal to exceed 32760
                    if val > 0:
                        val = 32765
                    else:
                        val = -32765
                frames.append(val.to_bytes(2, byteorder="little", signed=True))
            wf.writeframes(b"".join(frames))
        return wav_path

    def test_wav_stats_normal(self):
        # Create 1s normal sine wave with peak amplitude ~10000 (about -10 dBFS peak)
        wav_path = self.create_dummy_wav("normal.wav", amplitude=10000, duration_sec=1.0)
        stats = audio_quality_stats.wav_stats(wav_path)
        
        self.assertEqual(stats["sample_rate"], 16000)
        self.assertEqual(stats["channels"], 1)
        self.assertAlmostEqual(stats["peak_dbfs"], 20 * math.log10(10000 / 32768), places=1)
        self.assertEqual(stats["clipping_ratio"], 0.0)

    def test_wav_stats_clipping(self):
        # Create heavily clipped wave
        wav_path = self.create_dummy_wav("clipped.wav", amplitude=32767, duration_sec=0.5, clip=True)
        stats = audio_quality_stats.wav_stats(wav_path)
        
        self.assertGreater(stats["clipping_ratio"], 0.9) # clip true makes all samples clipped
        
    def test_quality_score(self):
        # Duration within boundaries (3s - 18s), no clipping, moderate rms
        row_good = {
            "duration_sec": 5.0,
            "rms_dbfs": -20.0,
            "clipping_ratio": 0.0
        }
        score_good = audio_quality_stats.quality_score(row_good)
        self.assertEqual(score_good, 100.0)

        # Duration outside bounds
        row_bad_dur = {
            "duration_sec": 2.0,
            "rms_dbfs": -20.0,
            "clipping_ratio": 0.0
        }
        score_bad_dur = audio_quality_stats.quality_score(row_bad_dur)
        self.assertEqual(score_bad_dur, 85.0) # 100 - 15


class TestPilotStats(unittest.TestCase):
    def test_compute_stats(self):
        rows = [
            {"duration_sec": 5.0, "transcript": "کتاب", "speaker_id": "spk1", "source_id": "src1", "gender": "male"},
            {"duration_sec": 10.0, "transcript": "قلم", "speaker_id": "spk2", "source_id": "src1", "gender": "female"},
        ]
        stats = pilot_stats.compute_stats(rows)
        self.assertEqual(stats["segments"], 2)
        self.assertEqual(stats["speakers"], 2)
        self.assertEqual(stats["sources"], 1)
        self.assertAlmostEqual(stats["total_hours"], 15.0 / 3600, places=3)
        self.assertEqual(stats["gender_clip_counts"], {"female": 1, "male": 1})


class TestTextQualityStats(unittest.TestCase):
    def test_score_text_good_pashto(self):
        metrics = text_quality_stats.score_text("دا یو ښه Pashto نه، بلکې پښتو متن دی")

        self.assertGreater(metrics["text_quality_score"], 0.5)
        self.assertGreater(metrics["character_quality"], 0.9)
        self.assertEqual(metrics["transcript_normalized"], "دا یو ښه نه، بلکې پښتو متن دی")

    def test_score_text_repetition_penalty(self):
        repeated = text_quality_stats.score_text("کتاب کتاب کتاب کتاب کتاب")
        varied = text_quality_stats.score_text("دا یو ښه پښتو متن دی")

        self.assertLess(repeated["repetition_quality"], varied["repetition_quality"])

    def test_pick_text_prefers_prediction(self):
        field, text = text_quality_stats.pick_text(
            {"reference": "کتاب", "prediction": "قلم"},
            text_quality_stats.DEFAULT_TEXT_FIELDS,
        )

        self.assertEqual(field, "prediction")
        self.assertEqual(text, "قلم")


class TestExportManualReview(unittest.TestCase):
    def test_select_review_rows_prioritizes_low_scores(self):
        rows = [
            {"segment_id": "high", "text_quality_score": 0.95},
            {"segment_id": "low", "text_quality_score": 0.30},
            {"segment_id": "review", "text_quality_score": 0.70},
        ]

        selected = export_manual_review.select_review_rows(rows, limit=2)

        self.assertEqual([row["segment_id"] for row in selected], ["low", "review"])

    def test_review_row_defaults(self):
        row = export_manual_review.review_row(
            {
                "segment_id": "seg1",
                "audio_path": "audio.wav",
                "prediction": "دا پښتو دی",
                "transcript_normalized": "دا پښتو دی",
            }
        )

        self.assertEqual(row["review_status"], "pending")
        self.assertEqual(row["corrected_transcript"], "")
        self.assertEqual(row["prediction_normalized"], "دا پښتو دی")


class TestExportCommonVoice(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_build_common_voice_row_with_transcript(self):
        row = {
            "segment_id": "seg1",
            "source_id": "src1",
            "audio_id": "aud1",
            "audio_path": "data/processed/src1/segments/aud1/aud1_00000.wav",
            "start_time_sec": 0.0,
            "end_time_sec": 5.0,
            "duration_sec": 5.0,
            "transcript": "دا پښتو دی",
            "gender": "male",
            "dialect": "eastern",
            "split": "train",
        }
        cv_row = export_common_voice.build_common_voice_row(row, {}, {}, "ps")
        self.assertEqual(cv_row["segment_id"], "seg1")
        self.assertEqual(cv_row["path"], "aud1/aud1_00000.wav")
        self.assertEqual(cv_row["sentence"], "دا پښتو دی")
        self.assertEqual(cv_row["sentence_normalized"], "دا پښتو دی")
        self.assertEqual(cv_row["gender"], "male")
        self.assertEqual(cv_row["accent"], "eastern")
        self.assertEqual(cv_row["locale"], "ps")
        self.assertEqual(cv_row["split"], "train")

    def test_build_common_voice_row_uses_asr_prediction(self):
        row = {"segment_id": "seg1", "audio_path": "a.wav", "duration_sec": 3.0}
        asr_index = {"seg1": {"prediction": "اس ار پښتو"}}
        cv_row = export_common_voice.build_common_voice_row(row, asr_index, {}, "ps")
        self.assertEqual(cv_row["sentence"], "اس ار پښتو")

    def test_classify_validation(self):
        self.assertEqual(export_common_voice.classify_validation({"audio_quality_score": 95}), "validated")
        self.assertEqual(export_common_voice.classify_validation({"audio_quality_score": 80}), "other")
        self.assertEqual(export_common_voice.classify_validation({"audio_quality_score": 60}), "invalidated")

    def test_rebased_clip_path_detects_segments(self):
        self.assertEqual(
            export_common_voice.rebased_clip_path("data/processed/x/segments/y/z.wav"),
            Path("y/z.wav"),
        )

    def test_end_to_end_export(self):
        manifest_path = self.temp_path / "manifest.jsonl"
        manifest_path.write_text(
            json.dumps({
                "segment_id": "seg1",
                "source_id": "src1",
                "audio_id": "aud1",
                "audio_path": "data/processed/src1/segments/aud1/aud1_00000.wav",
                "duration_sec": 5.0,
                "audio_quality_score": 95,
                "transcript": "دا پښتو دی",
            }, ensure_ascii=False)
            + "\n",
            encoding="utf-8",
        )
        out_dir = self.temp_path / "cv"
        # Simulate CLI by calling main with parsed args.
        old_argv = sys.argv[:]
        try:
            sys.argv = [
                "export_common_voice.py",
                str(manifest_path),
                "--out-dir", str(out_dir),
                "--locale", "ps",
                "--source-name", "Test",
            ]
            export_common_voice.main()
        finally:
            sys.argv = old_argv
        self.assertTrue((out_dir / "validated.tsv").exists())
        self.assertTrue((out_dir / "README.md").exists())
            "--out-dir", str(out_dir),
            "--locale", "ps",
            "--source-name", "Test",
        ]
        export_common_voice.main()
        self.assertTrue((out_dir / "validated.tsv").exists())
        self.assertTrue((out_dir / "README.md").exists())


class TestValidateCommonVoice(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_validate_corpus_valid(self):
        corpus_dir = self.temp_path / "cv"
        corpus_dir.mkdir()
        (corpus_dir / "validated.tsv").write_text(
            "\t".join(validate_common_voice.EXPECTED_COLUMNS) + "\n"
            + "\t".join(["clip.wav", "sentence", "normalized", "0", "0", "", "", "", "ps", "seg1", "src1", "aud1", "0.0", "5.0", "5.0", "95", "0.9", "spk1", "train"]) + "\n",
            encoding="utf-8",
        )
        header_only = "\t".join(validate_common_voice.EXPECTED_COLUMNS) + "\n"
        for name in ["other.tsv", "invalidated.tsv", "reported.tsv"]:
            (corpus_dir / name).write_text(header_only, encoding="utf-8")
        (corpus_dir / "README.md").write_text("", encoding="utf-8")
        result = validate_common_voice.validate_corpus(corpus_dir)
        self.assertTrue(result["valid"])
        self.assertEqual(result["total_rows"], 1)

    def test_validate_corpus_missing_columns(self):
        corpus_dir = self.temp_path / "cv"
        corpus_dir.mkdir()
        (corpus_dir / "validated.tsv").write_text("path\tsentence\nclip.wav\tsentence\n", encoding="utf-8")
        for name in ["other.tsv", "invalidated.tsv", "reported.tsv", "README.md", "LICENSE.md", "CITATION.bib", "corpus_stats.json"]:
            (corpus_dir / name).write_text("", encoding="utf-8")
        (corpus_dir / "clips").mkdir()
        result = validate_common_voice.validate_corpus(corpus_dir)
        self.assertFalse(result["valid"])
        self.assertTrue(any("missing columns" in e for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()
