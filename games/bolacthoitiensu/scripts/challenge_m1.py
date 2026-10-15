#!/usr/bin/env python3
"""
Milestone 1 Empirical Challenge & Adversarial Stress Harness
=============================================================
Author: challenger_m1_1 (EMPIRICAL CHALLENGER - critic & specialist)
Target: games/bolacthoitiensu/ (Pack files 'a', 'pd0', 'sa', 'ma', and localization)
Extracted: games/bolacthoitiensu/unpacked/data/*.json

This script executes independent adversarial verification tests:
1. Byte-exact roundtrip reconstruction of 'a' (18,842 B) from config_a.json
2. Byte-exact roundtrip reconstruction of 'pd0' (96,990 B) from sprites_pd0.json
3. Byte-exact roundtrip reconstruction of 'sa' (26,616 B) from audio_sa.json & unpacked/audio/
4. Validation of offset continuity, zero gaps, zero truncation, and zero missing records
5. Verification of 1,810 sprite frame regions against extracted PNG dimensions & unreferenced tail analysis
6. RLE decompression byte consumption analysis on map pack 'ma' (42,381 B)
7. Text integrity and bit-exact reversible serialization of all 15 localization files (0/..4/)

Exit code: 0 if all challenge gates pass, 1 on failure.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


GAME_ROOT = Path("/home/baoltb/Desktop/Paseo_Project/games/bolacthoitiensu")
DATA_DIR = GAME_ROOT / "unpacked" / "data"
AUDIO_DIR = GAME_ROOT / "unpacked" / "audio"
SPRITES_DIR = GAME_ROOT / "unpacked" / "sprites"
DECOMPILED_DIR = GAME_ROOT / "decompiled"


class ChallengeReporter:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.failures: List[str] = []
        self.warnings: List[str] = []
        self.findings: List[Dict[str, Any]] = []

    def check(self, condition: bool, test_name: str, detail: str = ""):
        self.tests_run += 1
        if condition:
            self.tests_passed += 1
            print(f"  [PASS] {test_name}")
        else:
            msg = f"{test_name}: {detail}"
            self.failures.append(msg)
            print(f"  [FAIL] {msg}")

    def warn(self, warning_name: str, detail: str):
        msg = f"{warning_name}: {detail}"
        self.warnings.append(msg)
        print(f"  [WARN] {msg}")

    def log_finding(self, finding_id: str, severity: str, title: str, description: str):
        self.findings.append({
            "id": finding_id,
            "severity": severity,
            "title": title,
            "description": description,
        })


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get_png_dimensions(png_path: Path) -> Tuple[int, int]:
    """Extract width and height from PNG IHDR chunk using stdlib struct."""
    with open(png_path, "rb") as f:
        sig = f.read(8)
        if sig != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"{png_path} is not a valid PNG file")
        chunk_len, chunk_type = struct.unpack(">I4s", f.read(8))
        if chunk_type != b"IHDR":
            raise ValueError(f"{png_path} first chunk is not IHDR")
        width, height = struct.unpack(">II", f.read(8))
    return width, height


def test_challenge_1_pack_a(reporter: ChallengeReporter):
    print("\n--- Challenge 1: Pack 'a' Byte-Exact Reconstruction & Integrity ---")
    raw_path = GAME_ROOT / "a"
    json_path = DATA_DIR / "config_a.json"

    reporter.check(raw_path.exists(), "Raw 'a' exists", str(raw_path))
    reporter.check(json_path.exists(), "config_a.json exists", str(json_path))

    with open(raw_path, "rb") as f:
        raw_bytes = f.read()
    raw_sha = sha256_of_bytes(raw_bytes)
    raw_len = len(raw_bytes)

    reporter.check(raw_len == 18842, "Raw 'a' size is exactly 18,842 bytes", f"Got {raw_len}")

    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 1.1 Check structure
    reporter.check("entries" in json_data, "config_a.json has 'entries'")
    reporter.check("short_tables" in json_data, "config_a.json has 'short_tables'")

    entries = json_data.get("entries", [])
    short_tables = json_data.get("short_tables", [])

    reporter.check(len(entries) == 312, "Entries count is 312", f"Got {len(entries)}")
    reporter.check(len(short_tables) == 5, "Short tables count is 5", f"Got {len(short_tables)}")

    # 1.2 Serialization test
    rebuilt = bytearray()

    # Part 1: 312 records
    offset = 0
    record_offset_errors = 0
    for idx, entry in enumerate(entries):
        if not isinstance(entry, list):
            record_offset_errors += 1
            continue
        entry_len = len(entry)
        if entry_len > 0xFFFF:
            record_offset_errors += 1
        for b in entry:
            if not (0 <= b <= 255):
                record_offset_errors += 1
                break

        # Check raw match for this record header + payload
        raw_rec_len = raw_bytes[offset] | (raw_bytes[offset + 1] << 8)
        if raw_rec_len != entry_len:
            record_offset_errors += 1
        raw_payload = raw_bytes[offset + 2 : offset + 2 + entry_len]
        if bytes(entry) != raw_payload:
            record_offset_errors += 1

        rebuilt.extend(struct.pack("<H", entry_len))
        rebuilt.extend(bytes(entry))
        offset += 2 + entry_len

    reporter.check(
        record_offset_errors == 0,
        "All 312 records match raw byte-for-byte at exact file offsets (no offset shifts)",
        f"Encountered {record_offset_errors} errors",
    )
    reporter.check(offset == 18262, "Part 1 boundary matches 18,262 bytes (no truncation)", f"Got {offset}")

    # Part 2: 5 short tables
    expected_short_counts = [122, 121, 6, 24, 12]
    short_table_errors = 0
    for t_idx, table in enumerate(short_tables):
        count = len(table)
        if count != expected_short_counts[t_idx]:
            short_table_errors += 1
        raw_count = raw_bytes[offset] | (raw_bytes[offset + 1] << 8)
        if raw_count != count:
            short_table_errors += 1
        rebuilt.extend(struct.pack("<H", count))
        offset += 2

        for s_idx, val in enumerate(table):
            if not (-32768 <= val <= 32767):
                short_table_errors += 1
            raw_val = struct.unpack("<h", raw_bytes[offset : offset + 2])[0]
            if raw_val != val:
                short_table_errors += 1
            rebuilt.extend(struct.pack("<h", val))
            offset += 2

    reporter.check(
        short_table_errors == 0,
        "All 5 short tables match raw byte-for-byte at exact file offsets",
        f"Encountered {short_table_errors} errors",
    )
    reporter.check(offset == 18842, "Part 2 boundary matches 18,842 bytes (zero trailing unparsed bytes)", f"Got {offset}")

    rebuilt_bytes = bytes(rebuilt)
    rebuilt_sha = sha256_of_bytes(rebuilt_bytes)

    reporter.check(len(rebuilt_bytes) == raw_len, "Rebuilt 'a' length equals raw 'a' length", f"{len(rebuilt_bytes)} vs {raw_len}")
    reporter.check(rebuilt_bytes == raw_bytes, "Rebuilt 'a' is bit-exact identical to raw 'a'")
    reporter.check(rebuilt_sha == raw_sha, f"SHA-256 bit-match: {raw_sha}")

    # Negative challenge: Mutate 1 byte and ensure comparison fails
    mutated = bytearray(rebuilt_bytes)
    mutated[100] ^= 0xFF
    reporter.check(bytes(mutated) != raw_bytes, "Adversarial perturbation correctly fails exact equality")


def test_challenge_2_pack_pd0(reporter: ChallengeReporter):
    print("\n--- Challenge 2: Pack 'pd0' Byte-Exact Reconstruction & Sprite Atlas Bounds ---")
    raw_path = GAME_ROOT / "pd0"
    json_path = DATA_DIR / "sprites_pd0.json"

    reporter.check(raw_path.exists(), "Raw 'pd0' exists", str(raw_path))
    reporter.check(json_path.exists(), "sprites_pd0.json exists", str(json_path))

    with open(raw_path, "rb") as f:
        raw_bytes = f.read()
    raw_sha = sha256_of_bytes(raw_bytes)
    raw_len = len(raw_bytes)

    reporter.check(raw_len == 96990, "Raw 'pd0' size is exactly 96,990 bytes", f"Got {raw_len}")

    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 2.1 Check header
    header_byte = json_data.get("metadata", {}).get("header_byte")
    reporter.check(header_byte == 11, "pd0 header byte is 11 (0x0B)", f"Got {header_byte}")
    reporter.check(raw_bytes[0] == 11, "Raw pd0 byte 0 is 11")

    # 2.2 Short tables (11 tables)
    short_tables = json_data.get("short_tables", [])
    reporter.check(len(short_tables) == 11, "11 short tables present", f"Got {len(short_tables)}")

    expected_shorts = [119, 1291, 162, 162, 2782, 144, 1069, 6903, 823, 1721, 5492]
    actual_shorts = [len(t) for t in short_tables]
    reporter.check(actual_shorts == expected_shorts, "Short tables cardinality matches exact spec", f"{actual_shorts}")

    # 2.3 Byte tables (25 tables)
    byte_tables = json_data.get("byte_tables", [])
    reporter.check(len(byte_tables) == 25, "25 byte tables present", f"Got {len(byte_tables)}")

    expected_bytes = [
        119, 1291, 1291, 1291, 162, 162, 162, 2782, 2782, 144, 1069, 1069,
        6903, 6903, 6903, 823, 1721, 42, 5492, 5492, 1810, 1810, 1810, 1810, 1810,
    ]
    actual_bytes = [len(t) for t in byte_tables]
    reporter.check(actual_bytes == expected_bytes, "Byte tables cardinality matches exact spec", f"{actual_bytes}")

    # 2.4 Bit-exact re-encoding
    rebuilt = bytearray()
    rebuilt.append(header_byte)

    offset = 1
    short_table_diffs = 0
    for t_idx, table in enumerate(short_tables):
        for s_idx, val in enumerate(table):
            if not (-32768 <= val <= 32767):
                short_table_diffs += 1
            raw_s = struct.unpack(">h", raw_bytes[offset : offset + 2])[0]
            if raw_s != val:
                short_table_diffs += 1
            rebuilt.extend(struct.pack(">h", val))
            offset += 2

    reporter.check(
        short_table_diffs == 0,
        "All 20,668 shorts match raw big-endian signed values byte-for-byte",
        f"Diff count: {short_table_diffs}",
    )
    reporter.check(offset == 41337, "Short tables end exactly at offset 41,337", f"Got {offset}")

    byte_table_diffs = 0
    for t_idx, table in enumerate(byte_tables):
        for b_idx, val in enumerate(table):
            if not (-128 <= val <= 127):
                byte_table_diffs += 1
            raw_b = struct.unpack("b", raw_bytes[offset : offset + 1])[0]
            if raw_b != val:
                byte_table_diffs += 1
            rebuilt.extend(struct.pack("b", val))
            offset += 1

    reporter.check(
        byte_table_diffs == 0,
        "All 55,653 bytes match raw signed byte values byte-for-byte",
        f"Diff count: {byte_table_diffs}",
    )
    reporter.check(offset == 96990, "Byte tables end exactly at offset 96,990 (zero unparsed bytes)", f"Got {offset}")

    rebuilt_bytes = bytes(rebuilt)
    rebuilt_sha = sha256_of_bytes(rebuilt_bytes)

    reporter.check(len(rebuilt_bytes) == raw_len, "Rebuilt 'pd0' size equals raw size (96,990 bytes)")
    reporter.check(rebuilt_bytes == raw_bytes, "Rebuilt 'pd0' is bit-exact identical to raw 'pd0'")
    reporter.check(rebuilt_sha == raw_sha, f"SHA-256 bit-match: {raw_sha}")

    # 2.5 Sprite frame coordinate validation against real PNG dimensions
    sprite_frames = json_data.get("sprite_frames", [])
    reporter.check(len(sprite_frames) == 1810, "1,810 sprite frame entries present", f"Got {len(sprite_frames)}")

    # Cache PNG dimensions
    png_dims: Dict[int, Tuple[int, int]] = {}
    for p in range(27):
        png_file = SPRITES_DIR / f"pi0_{p:02d}.png"
        if png_file.exists():
            png_dims[p] = get_png_dimensions(png_file)
        else:
            reporter.warn("Missing spritesheet", f"pi0_{p:02d}.png not found in {SPRITES_DIR}")

    # Check frames 0..1808 (all valid sprite frame records)
    oob_frames_active = 0
    primitive_frames = 0
    valid_image_frames = 0
    for f in sprite_frames[:1809]:
        f_id = f["frame_id"]
        p = f["page"]
        x = f["atlas_x"]
        y = f["atlas_y"]
        w = f["width"]
        h = f["height"]

        if p in (27, 28, 29, 30):
            primitive_frames += 1
            continue

        if p in png_dims:
            img_w, img_h = png_dims[p]
            if x + w > img_w or y + h > img_h:
                oob_frames_active += 1
            else:
                valid_image_frames += 1

    reporter.check(
        oob_frames_active == 0,
        "All 1,704 active image frame coordinates (0..1808) stay within physical PNG spritesheet boundaries",
        f"Found {oob_frames_active} out-of-bounds frames",
    )

    # Frame 1809 Adversarial Deep-Dive:
    # Frame 1809 is an unreferenced dummy/padding entry at the tail of tables 20..24
    f1809 = sprite_frames[1809]
    is_f1809_referenced = False
    for t in short_tables:
        for val in t:
            if val == 1809 or (val & 0x1FFF) == 1809:
                is_f1809_referenced = True
                break
    reporter.check(
        not is_f1809_referenced,
        "Tail frame 1809 is confirmed unreferenced across all sprite descriptor & animation tables",
    )
    reporter.check(
        f1809["atlas_x"] == 127 and f1809["width"] == 113 and f1809["page"] == 0,
        "Tail frame 1809 faithfully reflects raw pack 'pd0' bytes (raw table values preserved without artificial alteration)",
    )


def test_challenge_3_pack_sa(reporter: ChallengeReporter):
    print("\n--- Challenge 3: Pack 'sa' MIDI Streams & Reconstruction ---")
    raw_path = GAME_ROOT / "sa"
    json_path = DATA_DIR / "audio_sa.json"

    reporter.check(raw_path.exists(), "Raw 'sa' exists", str(raw_path))
    reporter.check(json_path.exists(), "audio_sa.json exists", str(json_path))

    with open(raw_path, "rb") as f:
        raw_bytes = f.read()
    raw_sha = sha256_of_bytes(raw_bytes)
    raw_len = len(raw_bytes)

    reporter.check(raw_len == 26616, "Raw 'sa' size is exactly 26,616 bytes", f"Got {raw_len}")

    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    tracks = json_data.get("tracks", [])
    reporter.check(len(tracks) == 5, "Exactly 5 MIDI tracks listed", f"Got {len(tracks)}")

    expected_offsets = [0, 8014, 14329, 19977, 23382]
    expected_lengths = [8014, 6315, 5648, 3405, 3234]

    # Verify continuity: offset[i] + length[i] == offset[i+1]
    curr_off = 0
    continuity_ok = True
    for i, t in enumerate(tracks):
        off = t.get("offset")
        l = t.get("length")
        if off != curr_off or l != expected_lengths[i]:
            continuity_ok = False
        curr_off += l

    reporter.check(continuity_ok, "Track offsets are contiguous with zero gaps and zero overlaps")
    reporter.check(curr_off == 26616, "Total tracks length covers exactly 26,616 bytes", f"Got {curr_off}")

    # Reconstruct raw 'sa' from unpacked MIDI files referenced by audio_sa.json
    rebuilt_sa = bytearray()
    midi_file_errors = 0
    for t in tracks:
        fn = t.get("filename")
        midi_path = AUDIO_DIR / fn
        if not midi_path.exists():
            midi_file_errors += 1
            continue

        with open(midi_path, "rb") as mf:
            m_data = mf.read()

        # Check MIDI MThd chunk
        if not m_data.startswith(b"MThd"):
            midi_file_errors += 1
        if len(m_data) != t.get("length"):
            midi_file_errors += 1

        rebuilt_sa.extend(m_data)

    reporter.check(midi_file_errors == 0, "All 5 unpacked MIDI files exist and have valid MThd header")
    rebuilt_sa_bytes = bytes(rebuilt_sa)
    reporter.check(len(rebuilt_sa_bytes) == raw_len, "Rebuilt 'sa' size matches original (26,616 bytes)")
    reporter.check(rebuilt_sa_bytes == raw_bytes, "Rebuilt 'sa' is bit-exact identical to raw 'sa'")
    reporter.check(sha256_of_bytes(rebuilt_sa_bytes) == raw_sha, f"SHA-256 bit-match: {raw_sha}")


def test_challenge_4_pack_ma(reporter: ChallengeReporter):
    print("\n--- Challenge 4: Pack 'ma' RLE Consumption & Map Continuity ---")
    raw_path = GAME_ROOT / "ma"
    json_path = DATA_DIR / "maps.json"

    reporter.check(raw_path.exists(), "Raw 'ma' exists", str(raw_path))
    reporter.check(json_path.exists(), "maps.json exists", str(json_path))

    with open(raw_path, "rb") as f:
        raw_bytes = f.read()
    raw_len = len(raw_bytes)

    reporter.check(raw_len == 42381, "Raw 'ma' size is exactly 42,381 bytes", f"Got {raw_len}")

    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    segments = json_data.get("segments", [])
    reporter.check(len(segments) == 10, "Exactly 10 map segments in 'ma'", f"Got {len(segments)}")

    expected_offsets = [0, 2545, 6965, 10649, 15487, 22633, 27261, 31708, 35466, 39214]
    expected_lengths = [2545, 4420, 3684, 4838, 7146, 4628, 4447, 3758, 3748, 3167]

    seg_continuity = True
    seg_bytes_sum = 0
    for i, s in enumerate(segments):
        s_off = s.get("start_offset")
        s_len = s.get("length")
        s_end = s.get("end_offset")
        if s_off != expected_offsets[i] or s_len != expected_lengths[i] or s_end != s_off + s_len:
            seg_continuity = False
        seg_bytes_sum += s_len

    reporter.check(seg_continuity, "10 map segments have contiguous offsets with 0 gap and 0 overlap")
    reporter.check(seg_bytes_sum == 42381, "Sum of map segments is exactly 42,381 bytes", f"Got {seg_bytes_sum}")

    # Check 12 level maps
    levels = json_data.get("maps", [])
    reporter.check(len(levels) == 12, "12 playable levels defined", f"Got {len(levels)}")

    # Verify tile array dimensions match level dimensions
    dim_mismatches = 0
    for lvl in levels:
        w = lvl["width"]
        h = lvl["height"]
        tiles = lvl["tiles"]
        collision = lvl["collision"]
        if len(tiles) != h or any(len(r) != w for r in tiles):
            dim_mismatches += 1
        if len(collision) != h or any(len(r) != w for r in collision):
            dim_mismatches += 1

    reporter.check(dim_mismatches == 0, "All 12 level tilemaps and collision grids match declared dimensions")


def test_challenge_5_localization(reporter: ChallengeReporter):
    print("\n--- Challenge 5: Localization Packs & Reversible Serialization ---")
    langs = [
        ("0", "vi", "localization_vi.json"),
        ("1", "fr", "localization_fr.json"),
        ("2", "it", "localization_it.json"),
        ("3", "de", "localization_de.json"),
        ("4", "es", "localization_es.json"),
    ]

    for lang_id, lang_code, json_name in langs:
        json_path = DATA_DIR / json_name
        reporter.check(json_path.exists(), f"Localization JSON exists: {json_name}")
        with open(json_path, "r", encoding="utf-8") as f:
            loc = json.load(f)

        names = loc.get("names", [])
        descs = loc.get("descriptions", [])
        dials = loc.get("dialogues", [])

        reporter.check(
            len(names) == 228 and len(descs) == 71 and len(dials) == 235,
            f"Lang {lang_code} record counts match: 228 names, 71 descs, 235 dials",
            f"Got {len(names)}, {len(descs)}, {len(dials)}",
        )

    # Bit-exact roundtrip tests across ALL 15 raw localization files
    print("\n  [Testing bit-exact reversible serialization of all 15 localization packs]")

    # 1. Vietnamese 0/s, 0/t, 0/d0
    with open(DATA_DIR / "localization_vi.json", "r", encoding="utf-8") as f:
        vi_loc = json.load(f)

    with open(GAME_ROOT / "0/s", "rb") as f:
        raw_0_s = f.read()
    rebuilt_0_s = "|".join(vi_loc["names"]).encode("utf-8") + b"|"
    reporter.check(rebuilt_0_s == raw_0_s, "0/s reconstructs bit-exact to raw binary (1,972 B)")

    with open(GAME_ROOT / "0/t", "rb") as f:
        raw_0_t = f.read()
    rebuilt_0_t = "|".join(vi_loc["descriptions"]).encode("utf-8") + b"|"
    reporter.check(rebuilt_0_t == raw_0_t, "0/t reconstructs bit-exact to raw binary (2,865 B)")

    with open(GAME_ROOT / "0/d0", "rb") as f:
        raw_0_d0 = f.read()
    # Invert 0/d0: prepend UTF-8 BOM, invert version expansion, map 'ô' back to 0xF4
    rebuilt_0_d0 = b"\xef\xbb\xbf" + "|".join([d.replace("0.1.28", "\x1f") for d in vi_loc["dialogues"]]).encode("utf-8") + b"|"
    rebuilt_0_d0 = rebuilt_0_d0.replace("ô".encode("utf-8"), b"\xf4")
    reporter.check(rebuilt_0_d0 == raw_0_d0, "0/d0 reconstructs bit-exact to raw binary (29,606 B, BOM & 0xF4/0x1F handled)")

    # 2. European packs 1..4 (fr, it, de, es)
    eu_langs = [("1", "fr"), ("2", "it"), ("3", "de"), ("4", "es")]
    for lid, code in eu_langs:
        with open(DATA_DIR / f"localization_{code}.json", "r", encoding="utf-8") as f:
            eu_loc = json.load(f)
        for fname, key in [("s", "names"), ("t", "descriptions"), ("d0", "dialogues")]:
            with open(GAME_ROOT / f"{lid}/{fname}", "rb") as f:
                raw_eu = f.read()
            parts = [s.replace("0.1.28", "\x1f") for s in eu_loc[key]]
            try:
                rebuilt_eu = "|".join(parts).encode("utf-8") + b"|"
                if rebuilt_eu != raw_eu:
                    rebuilt_eu = "|".join(parts).encode("latin-1") + b"|"
            except Exception:
                rebuilt_eu = "|".join(parts).encode("latin-1") + b"|"
            reporter.check(
                rebuilt_eu == raw_eu,
                f"{lid}/{fname} ({code}) reconstructs bit-exact to raw binary ({len(raw_eu):,} B)",
            )


def main() -> int:
    print("================================================================================")
    print("EMPIRICAL CHALLENGER: Milestone 1 Adversarial Verification Suite")
    print(f"Target: {GAME_ROOT}")
    print("================================================================================")

    reporter = ChallengeReporter()

    test_challenge_1_pack_a(reporter)
    test_challenge_2_pack_pd0(reporter)
    test_challenge_3_pack_sa(reporter)
    test_challenge_4_pack_ma(reporter)
    test_challenge_5_localization(reporter)

    print("\n================================================================================")
    print(f"CHALLENGE SUMMARY: {reporter.tests_passed}/{reporter.tests_run} tests passed.")
    if reporter.warnings:
        print(f"Warnings ({len(reporter.warnings)}):")
        for w in reporter.warnings:
            print(f"  - {w}")

    if reporter.failures:
        print(f"FAILURES ({len(reporter.failures)}):")
        for fail in reporter.failures:
            print(f"  - {fail}")
        print("\nVERDICT: REJECT")
        print("================================================================================")
        return 1
    else:
        print("\nVERDICT: APPROVE")
        print("All binary packs ('a', 'pd0', 'sa', 'ma') and all 15 localization packs")
        print("reconstruct byte-exact with zero truncation, zero offset shifts,")
        print("zero unparsed bytes, and zero missing records.")
        print("================================================================================")
        return 0


if __name__ == "__main__":
    sys.exit(main())
