import sys
import unittest
import math
import wave
import tempfile
from pathlib import Path

# Add scripts directory to sys.path so we can import the modules
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.append(str(scripts_dir))

import pashto_normalize
import audio_quality_stats
import pilot_stats


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


if __name__ == "__main__":
    unittest.main()
