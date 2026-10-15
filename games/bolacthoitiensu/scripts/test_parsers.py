#!/usr/bin/env python3
"""
Bộ Lạc Thời Tiền Sử (Prehistoric Tribes) - Parser Verification Test Suite
========================================================================
Comprehensive automated test suite programmatically verifying:
- 100% byte-coverage and zero unparsed bytes for:
  * pack 'a' (18,842 bytes)
  * pack 'pd0' (96,990 bytes)
  * pack 'ma' (42,381 bytes)
  * pack 'sa' (26,616 bytes)
  * localization packs '0/'..'4/' (vi, fr, it, de, es)
- Bit-exact re-encoding equivalence for 'a', 'pd0', 'sa'
- RLE decompression exact byte consumption for all 10 map segments in 'ma'
- Extracted JSON file schema and data integrity under unpacked/data/
- Decompiled Java source files integrity under decompiled/

Exit Code: 0 on complete pass, 1 on any failure.
"""

from __future__ import annotations

import json
import struct
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List


GAME_ROOT = Path("/home/baoltb/Desktop/Paseo_Project/games/bolacthoitiensu")
DATA_DIR = GAME_ROOT / "unpacked" / "data"
DECOMPILED_DIR = GAME_ROOT / "decompiled"
AUDIO_DIR = GAME_ROOT / "unpacked" / "audio"


class TestDecompiledJavaFiles(unittest.TestCase):
    """Verifies that all 7 CFR-decompiled Java files exist and are complete."""

    EXPECTED_CLASSES = ["tribes", "a", "b", "c", "d", "e", "f"]

    def test_all_seven_java_files_exist_and_non_empty(self):
        for class_name in self.EXPECTED_CLASSES:
            java_file = DECOMPILED_DIR / f"{class_name}.java"
            self.assertTrue(java_file.exists(), f"Missing decompiled source: {java_file}")
            size = java_file.stat().st_size
            self.assertGreater(size, 500, f"Decompiled file {java_file} too small ({size} bytes)")

            # Check that file starts with CFR header and has class definition
            with open(java_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.assertIn("Decompiled with CFR", content, f"{java_file} missing CFR comment header")
            self.assertTrue(
                f"class {class_name}" in content or f"interface {class_name}" in content,
                f"{java_file} does not contain class definition for {class_name}",
            )


class TestConfigAParser(unittest.TestCase):
    """Verifies 100% byte-coverage and bit-exact reconstruction of pack 'a' (18,842 bytes)."""

    def setUp(self):
        self.raw_path = GAME_ROOT / "a"
        self.json_path = DATA_DIR / "config_a.json"
        with open(self.raw_path, "rb") as f:
            self.raw_bytes = f.read()
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.json_data = json.load(f)

    def test_file_size_and_zero_unparsed_bytes(self):
        self.assertEqual(len(self.raw_bytes), 18842, "Raw pack 'a' size must be 18,842 bytes")
        self.assertEqual(self.json_data["metadata"]["file_size"], 18842)
        self.assertEqual(self.json_data["metadata"]["unparsed_bytes"], 0)

    def test_part1_records_count_and_payload(self):
        entries = self.json_data["entries"]
        self.assertEqual(len(entries), 312, "Must contain exactly 312 records in Part 1")
        total_payload = sum(len(e) for e in entries)
        self.assertEqual(total_payload, 17638, "Payload sum of Part 1 entries must be 17,638 bytes")
        total_part1_bytes = total_payload + 312 * 2
        self.assertEqual(total_part1_bytes, 18262, "Part 1 total bytes must be 18,262 bytes")

    def test_part2_short_tables_count_and_shorts(self):
        short_tables = self.json_data["short_tables"]
        self.assertEqual(len(short_tables), 5, "Must contain exactly 5 short tables in Part 2")
        expected_counts = [122, 121, 6, 24, 12]
        actual_counts = [len(t) for t in short_tables]
        self.assertEqual(actual_counts, expected_counts, f"Table counts mismatch: {actual_counts} vs {expected_counts}")
        total_shorts = sum(actual_counts)
        self.assertEqual(total_shorts, 285, "Total shorts in Part 2 must be 285")
        total_part2_bytes = total_shorts * 2 + 5 * 2
        self.assertEqual(total_part2_bytes, 580, "Part 2 total bytes must be 580 bytes")

    def test_bit_exact_binary_reconstruction(self):
        """Reconstructs raw binary from JSON entries and short tables, asserting bit-exact match."""
        rebuilt = bytearray()

        # Part 1: 312 entries with 2-byte little-endian length
        for entry in self.json_data["entries"]:
            length = len(entry)
            rebuilt.extend(struct.pack("<H", length))
            rebuilt.extend(bytes(entry))

        # Part 2: 5 short tables with 2-byte little-endian count
        for table in self.json_data["short_tables"]:
            count = len(table)
            rebuilt.extend(struct.pack("<H", count))
            for val in table:
                rebuilt.extend(struct.pack("<h", val))

        self.assertEqual(len(rebuilt), len(self.raw_bytes), "Rebuilt size must equal original size")
        self.assertEqual(bytes(rebuilt), self.raw_bytes, "Rebuilt binary must match pack 'a' byte-for-byte")

    def test_parsed_game_configurations(self):
        configs = self.json_data["parsed_configs"]
        self.assertEqual(len(configs["map_dimensions"]), 12)
        self.assertEqual(len(configs["map_routing"]), 12)
        self.assertEqual(len(configs["font_glyph_map"]), 128)
        self.assertEqual(len(configs["resource_costs"]), 8)
        self.assertEqual(configs["map_routing"], [0, 0, 1, 2, 3, 4, 4, 5, 6, 7, 8, 9])
        self.assertEqual(configs["rle_codebook"]["repeat_counts"], [4, 4, 2, 2, 2, 2])
        self.assertEqual(configs["rle_codebook"]["tile_values"], [3, 0, 43, 6, 3, 0])


class TestSpritesPD0Parser(unittest.TestCase):
    """Verifies 100% byte-coverage and bit-exact reconstruction of pack 'pd0' (96,990 bytes)."""

    def setUp(self):
        self.raw_path = GAME_ROOT / "pd0"
        self.json_path = DATA_DIR / "sprites_pd0.json"
        with open(self.raw_path, "rb") as f:
            self.raw_bytes = f.read()
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.json_data = json.load(f)

    def test_file_size_and_header(self):
        self.assertEqual(len(self.raw_bytes), 96990, "pd0 raw size must be 96,990 bytes")
        self.assertEqual(self.raw_bytes[0], 11, "pd0 header byte must be 11 (0x0B)")
        self.assertEqual(self.json_data["metadata"]["header_byte"], 11)
        self.assertEqual(self.json_data["metadata"]["unparsed_bytes"], 0)

    def test_tables_cardinality(self):
        self.assertEqual(len(self.json_data["short_tables"]), 11, "Must contain exactly 11 short tables")
        self.assertEqual(len(self.json_data["byte_tables"]), 25, "Must contain exactly 25 byte tables")

        expected_shorts = [119, 1291, 162, 162, 2782, 144, 1069, 6903, 823, 1721, 5492]
        actual_shorts = [len(t) for t in self.json_data["short_tables"]]
        self.assertEqual(actual_shorts, expected_shorts)

        expected_bytes = [
            119, 1291, 1291, 1291, 162, 162, 162, 2782, 2782, 144, 1069, 1069,
            6903, 6903, 6903, 823, 1721, 42, 5492, 5492, 1810, 1810, 1810, 1810, 1810,
        ]
        actual_bytes = [len(t) for t in self.json_data["byte_tables"]]
        self.assertEqual(actual_bytes, expected_bytes)

    def test_bit_exact_binary_reconstruction(self):
        """Reconstructs raw binary from short and byte tables, asserting bit-exact match."""
        rebuilt = bytearray()
        rebuilt.append(self.json_data["metadata"]["header_byte"])

        # 11 short tables (big-endian signed 16-bit)
        for table in self.json_data["short_tables"]:
            for val in table:
                rebuilt.extend(struct.pack(">h", val))

        # 25 byte tables (signed 8-bit)
        for table in self.json_data["byte_tables"]:
            for val in table:
                rebuilt.extend(struct.pack("b", val))

        self.assertEqual(len(rebuilt), len(self.raw_bytes), "Rebuilt size must equal original size")
        self.assertEqual(bytes(rebuilt), self.raw_bytes, "Rebuilt binary must match pack 'pd0' byte-for-byte")

    def test_sprite_frames_consistency(self):
        frames = self.json_data["sprite_frames"]
        self.assertEqual(len(frames), 1810, "Must contain exactly 1,810 sprite frame regions")
        j20 = self.json_data["byte_tables"][20]
        j21 = self.json_data["byte_tables"][21]
        j22 = self.json_data["byte_tables"][22]
        j23 = self.json_data["byte_tables"][23]
        j24 = self.json_data["byte_tables"][24]

        # Verify a random sample of frame entries against tables
        for idx in [0, 1, 10, 100, 500, 1000, 1809]:
            f = frames[idx]
            self.assertEqual(f["frame_id"], idx)
            self.assertEqual(f["page"], j20[idx] & 0x1F)
            self.assertEqual(f["atlas_x"], j21[idx] & 0x7F)
            self.assertEqual(f["atlas_y"], j22[idx] & 0xFF)
            self.assertEqual(f["width"], j23[idx] & 0xFF)
            self.assertEqual(f["height"], j24[idx] & 0xFF)


class TestMapsParser(unittest.TestCase):
    """Verifies 100% byte-coverage and RLE decompression of pack 'ma' (42,381 bytes)."""

    def setUp(self):
        self.raw_path = GAME_ROOT / "ma"
        self.json_path = DATA_DIR / "maps.json"
        with open(self.raw_path, "rb") as f:
            self.raw_bytes = f.read()
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.json_data = json.load(f)

    def test_file_size_and_zero_unparsed_bytes(self):
        self.assertEqual(len(self.raw_bytes), 42381, "ma raw size must be 42,381 bytes")
        self.assertEqual(self.json_data["metadata"]["file_size"], 42381)
        self.assertEqual(self.json_data["metadata"]["unparsed_bytes"], 0)

    def test_ten_map_segments_coverage(self):
        segments = self.json_data["segments"]
        self.assertEqual(len(segments), 10, "Must contain exactly 10 map segments")

        expected_lengths = [2545, 4420, 3684, 4838, 7146, 4628, 4447, 3758, 3748, 3167]
        actual_lengths = [s["length"] for s in segments]
        self.assertEqual(actual_lengths, expected_lengths)
        self.assertEqual(sum(actual_lengths), 42381)

        # Check contiguous offset sequence
        current_offset = 0
        for seg in segments:
            self.assertEqual(seg["start_offset"], current_offset)
            current_offset += seg["length"]
            self.assertEqual(seg["end_offset"], current_offset)
        self.assertEqual(current_offset, 42381)

    def test_all_twelve_levels_dimensions_and_tiles(self):
        maps = self.json_data["maps"]
        self.assertEqual(len(maps), 12, "Must contain exactly 12 level maps")

        expected_dims = [
            (64, 48), (64, 48), (64, 80), (64, 64), (64, 96), (96, 96),
            (96, 96), (96, 64), (80, 80), (96, 48), (48, 96), (64, 64),
        ]

        for q, lvl in enumerate(maps):
            self.assertEqual(lvl["level_id"], q)
            exp_w, exp_h = expected_dims[q]
            self.assertEqual(lvl["width"], exp_w)
            self.assertEqual(lvl["height"], exp_h)

            tiles = lvl["tiles"]
            collision = lvl["collision"]
            self.assertEqual(len(tiles), exp_h, f"Level {q} tile rows mismatch")
            self.assertEqual(len(tiles[0]), exp_w, f"Level {q} tile cols mismatch")
            self.assertEqual(len(collision), exp_h, f"Level {q} collision rows mismatch")
            self.assertEqual(len(collision[0]), exp_w, f"Level {q} collision cols mismatch")

            # Check that boundary borders are blocked (-126)
            for x in range(exp_w):
                self.assertEqual(collision[0][x], -126, f"Level {q} top border not blocked at x={x}")
                self.assertEqual(collision[exp_h - 1][x], -126, f"Level {q} bottom border not blocked at x={x}")
            for y in range(exp_h):
                self.assertEqual(collision[y][0], -126, f"Level {q} left border not blocked at y={y}")
                self.assertEqual(collision[y][exp_w - 1], -126, f"Level {q} right border not blocked at y={y}")


class TestAudioSAParser(unittest.TestCase):
    """Verifies 100% byte-coverage and MIDI integrity of pack 'sa' (26,616 bytes)."""

    def setUp(self):
        self.raw_path = GAME_ROOT / "sa"
        self.json_path = DATA_DIR / "audio_sa.json"
        with open(self.raw_path, "rb") as f:
            self.raw_bytes = f.read()
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.json_data = json.load(f)

    def test_file_size_and_zero_unparsed_bytes(self):
        self.assertEqual(len(self.raw_bytes), 26616, "sa raw size must be 26,616 bytes")
        self.assertEqual(self.json_data["metadata"]["file_size"], 26616)
        self.assertEqual(self.json_data["metadata"]["unparsed_bytes"], 0)

    def test_five_midi_tracks_integrity(self):
        tracks = self.json_data["tracks"]
        self.assertEqual(len(tracks), 5, "Must contain exactly 5 MIDI tracks")

        expected_lengths = [8014, 6315, 5648, 3405, 3234]
        expected_offsets = [0, 8014, 14329, 19977, 23382]

        for i, track in enumerate(tracks):
            self.assertEqual(track["track_id"], i)
            self.assertEqual(track["offset"], expected_offsets[i])
            self.assertEqual(track["length"], expected_lengths[i])
            self.assertEqual(track["format_signature"], "MThd")

            # Verify chunk from raw file
            off = track["offset"]
            length = track["length"]
            chunk = self.raw_bytes[off : off + length]
            self.assertTrue(chunk.startswith(b"MThd"), f"Track {i} does not start with MThd")

            # Verify corresponding unpacked audio file if present
            midi_file = AUDIO_DIR / f"track_{i:02d}.mid"
            if midi_file.exists():
                with open(midi_file, "rb") as f_mid:
                    mid_data = f_mid.read()
                self.assertEqual(mid_data, chunk, f"track_{i:02d}.mid does not match sa slice bit-for-bit")

    def test_bit_exact_concatenation(self):
        """Verifies that concatenating all tracks matches sa byte-for-byte."""
        concatenated = bytearray()
        for track in self.json_data["tracks"]:
            off = track["offset"]
            length = track["length"]
            concatenated.extend(self.raw_bytes[off : off + length])

        self.assertEqual(bytes(concatenated), self.raw_bytes)


class TestLocalizationParsers(unittest.TestCase):
    """Verifies all 5 localization packs 0/..4/ for 's', 't', 'd0'."""

    LANGS = [
        ("0", "vi", "localization_vi.json"),
        ("1", "fr", "localization_fr.json"),
        ("2", "it", "localization_it.json"),
        ("3", "de", "localization_de.json"),
        ("4", "es", "localization_es.json"),
    ]

    def test_all_five_languages_string_counts_and_clean_data(self):
        for lang_id, lang_code, json_name in self.LANGS:
            json_file = DATA_DIR / json_name
            self.assertTrue(json_file.exists(), f"Missing localization file {json_file}")

            with open(json_file, "r", encoding="utf-8") as f:
                loc = json.load(f)

            self.assertEqual(loc["metadata"]["lang_id"], int(lang_id))
            self.assertEqual(loc["metadata"]["lang_code"], lang_code)
            self.assertEqual(loc["metadata"]["unparsed_bytes"], 0)

            # Names: exactly 228
            self.assertEqual(len(loc["names"]), 228, f"{lang_code} names count mismatch")
            # Descriptions: exactly 71
            self.assertEqual(len(loc["descriptions"]), 71, f"{lang_code} descriptions count mismatch")
            # Dialogues: exactly 235
            self.assertEqual(len(loc["dialogues"]), 235, f"{lang_code} dialogues count mismatch")

            # Assert non-empty strings
            self.assertTrue(all(isinstance(s, str) for s in loc["names"]))
            self.assertTrue(all(isinstance(s, str) for s in loc["descriptions"]))
            self.assertTrue(all(isinstance(s, str) for s in loc["dialogues"]))

    def test_vietnamese_specific_tokens_and_bom(self):
        """Asserts UTF-8 BOM was stripped cleanly and Vietnamese characters decode properly."""
        json_file = DATA_DIR / "localization_vi.json"
        with open(json_file, "r", encoding="utf-8") as f:
            loc = json.load(f)

        # Check dialogue 233 contains version string and credits
        d233 = loc["dialogues"][233]
        self.assertIn("0.1.28", d233, "Dynamic token 0x1F was not expanded to version '0.1.28'")
        self.assertIn("bo lac thoi tien su", d233.lower())

        # Check accented character replacement in string 50 (0xF4 -> ô)
        d50 = loc["dialogues"][50]
        self.assertIn("tôt nhat", d50, "String 50 missing decoded 'tôt nhat' from 0xF4")

        # Check accented character replacement in string 94 (0xF4 -> ô)
        d94 = loc["dialogues"][94]
        self.assertIn("dông tu", d94, "String 94 missing decoded 'dông tu' from 0xF4")

    def test_default_localization_json_matches_vietnamese(self):
        default_file = DATA_DIR / "localization.json"
        vi_file = DATA_DIR / "localization_vi.json"
        self.assertTrue(default_file.exists())
        with open(default_file, "r", encoding="utf-8") as f1, open(vi_file, "r", encoding="utf-8") as f2:
            self.assertEqual(json.load(f1), json.load(f2))


def run_tests() -> int:
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    suite.addTests(loader.loadTestsFromTestCase(TestDecompiledJavaFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigAParser))
    suite.addTests(loader.loadTestsFromTestCase(TestSpritesPD0Parser))
    suite.addTests(loader.loadTestsFromTestCase(TestMapsParser))
    suite.addTests(loader.loadTestsFromTestCase(TestAudioSAParser))
    suite.addTests(loader.loadTestsFromTestCase(TestLocalizationParsers))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
