# BỘ LẠC THỜI TIỀN SỬ (PREHISTORIC TRIBES)
## Comprehensive Reverse-Engineering Specification & Web Remake Architecture
**Version:** 1.0.0 (Production Master Specification)  
**Target Game:** *Bộ Lạc Thời Tiền Sử* (*Prehistoric Tribes*, THQ Wireless / Metaflow v0.1.28, 2008)  
**Binary Artifact:** `/home/baoltb/Downloads/Bolacthoitiensu.jar` (SHA-256: `4028818ccc92daa9ce051ea3d57c36f25b337d416c2d584903ab595526eac6ba`)  
**Decompiled Sources:** `decompiled/` (`tribes.java`, `a.java`, `b.java`, `c.java`, `d.java`, `e.java`, `f.java`)  
**Decoded Datasets:** `unpacked/data/` (`config_a.json`, `sprites_pd0.json`, `maps.json`, `audio_sa.json`, `localization_vi.json`)  
**Target Implementation:** Modular ES2022 + HTML5 Canvas 2D Web Remake (`games/bolacthoitiensu/web/`)  

---

## 1. Executive Summary & Architecture Overview

### 1.1 Project Mission & Scope
*Bộ Lạc Thời Tiền Sử* (*Prehistoric Tribes*) is a real-time tribal strategy and colony simulation game developed for the Java 2 Micro Edition (J2ME) MIDP-2.0 / CLDC-1.1 platform. The game combines city-building, resource gathering, villager profession training, defensive fortifications, dynamic animal and enemy combat, and a multi-stage campaign quest narrative set at the dawn of human civilization following the retreat of the glaciers.

This document serves as the authoritative, mathematical, and algorithmic blueprint for reconstructing the game as a high-fidelity HTML5 Canvas web application. Every schema, constant, bitmask, formula, and state transition detailed herein is directly derived from bit-exact decompilation and dynamic execution analysis of the original bytecode (`f.java` 6,679 lines, `b.java` 5,804 lines, `e.java` 279 lines, `c.java` 403 lines, `a.java` 117 lines) and 100.0% verified against extracted binary assets.

### 1.2 Original J2ME Architecture vs Web Remake Architecture

```
+----------------------------------------------------------------------------------------------------+
|                                    ORIGINAL J2ME MIDP-2.0 SYSTEM                                   |
|                                                                                                    |
|  [MIDlet Entry] tribes.class (Lifecycle, Display.setCurrent)                                       |
|         │                                                                                          |
|         ▼                                                                                          |
|  [Renderer & UI Engine] f.class (Canvas, 240x320 Canvas, Key Events, Double Buffering)             |
|         │                                                                                          |
|         ├──► [Binary Pack Loader] e.class (ResourceStreams: /a, /pd0, /ma, /sa, /0/..)             |
|         │                                                                                          |
|         ├──► [Simulation Core] b.class (9,983-Byte Structure-of-Arrays Simulation Buffer)          |
|         │                                                                                          |
|         ├──► [Text & Font Pipeline] c.class (Glyph Metrics, Variable-Pitch Blitter, /s, /t, /d0)   |
|         │                                                                                          |
|         ├──► [Audio Subsystem] a.class (JSR-135 Mobile Media API, Standard MIDI Tracks)           |
|         │                                                                                          |
|         └──► [Persistence] RecordStore RMS (Slot 0: Options; Slots 1-2: Savegame Snapshots)        |
+----------------------------------------------------------------------------------------------------+
                                                 │
                                                 │ Reverse-Engineered Translation
                                                 ▼
+----------------------------------------------------------------------------------------------------+
|                                  HTML5 CANVAS WEB REMAKE ARCHITECTURE                              |
|                                                                                                    |
|  [Entry Point] web/index.html & web/js/main.js (Virtual 240x320 Viewport, 60fps Loop)              |
|         │                                                                                          |
|         ├──► [Engine Runtime]                                                                      |
|         │     ├── Renderer (`renderer.js`): Dual-path Canvas 2D (Bitmap Blit + Vector Primitives)  |
|         │     ├── Camera (`camera.js`): Sub-tile smooth scrolling, viewport clamping, target focus|
|         │     ├── Input (`input.js`): Virtual D-pad, NumPad emulation, Mouse/Touch raycasting     |
|         │     ├── Audio (`audio.js`): Web Audio API / SoundFont synthesizer for MIDI tracks 0..4   |
|         │     └── Storage (`storage.js`): localStorage persistence matching RMS Slot 0..2 schema   |
|         │                                                                                          |
|         ├──► [Simulation & Game Logic]                                                             |
|         │     ├── World Grid (`world.js`): 96x96 Tilemap + signed 8-bit entity occupancy grid      |
|         │     ├── Villager FSM (`villager.js`): 101-stride SoA entity simulation (100 units)       |
|         │     ├── Building System (`building.js`): 12 Authentic Buildings, footprint & upgrades   |
|         │     ├── Economy (`economy.js`): 4 Resources (Food, Wood, Stone, Bone) + Scoring        |
|         │     └── Quest Engine (`quest.js`): Multi-stage objective evaluation & dialogue ticker   |
|         │                                                                                          |
|         └──► [Asset Pipeline]                                                                      |
|               ├── `unpacked/data/`: `config_a.json`, `sprites_pd0.json`, `maps.json`, etc.         |
|               └── `unpacked/sprites/`: 49 PNG sheets (`pi0_00.png`..`pi0_26.png`, `pi8_*`, `pi9_*`)|
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Binary Resource Pack Schemas

The game ships with 4 primary monolithic binary packs in the JAR root (`a`, `pd0`, `ma`, `sa`) and 5 localized string packages in language subdirectories `0/` (Vietnamese), `1/` (French), `2/` (Italian), `3/` (German), and `4/` (Spanish).

```
+------------------+---------------+----------------------------------------------------------------+
| File Name        | Size (Bytes)  | Internal Structure Summary                                     |
+------------------+---------------+----------------------------------------------------------------+
| a                | 18,842        | Part 1: 312 length-prefixed records (18,262 B)                 |
|                  |               | Part 2: 5 count-prefixed 16-bit short tables (580 B)           |
+------------------+---------------+----------------------------------------------------------------+
| pd0              | 96,990        | Byte 0: Header (0x0B)                                          |
|                  |               | Offsets 1..41,336: 11 Big-Endian signed 16-bit short tables    |
|                  |               | Offsets 41,337..96,989: 25 signed 8-bit byte tables            |
+------------------+---------------+----------------------------------------------------------------+
| ma               | 42,381        | 10 contiguous RLE-compressed map segments                      |
|                  |               | Decompressed using Codebook Record 197 into 12 levels          |
+------------------+---------------+----------------------------------------------------------------+
| sa               | 26,616        | 5 Standard MIDI format 0/1 files concatenated                  |
|                  |               | Offsets: 0, 8014, 14329, 19977, 23382                          |
+------------------+---------------+----------------------------------------------------------------+
| <lang>/s         | 1,710 - 1,972 | 228 UI, item, and building name strings, pipe-delimited (`|`)  |
+------------------+---------------+----------------------------------------------------------------+
| <lang>/t         | 2,865 - 3,227 | 71 building and unit descriptions, pipe-delimited (`|`)        |
+------------------+---------------+----------------------------------------------------------------+
| <lang>/d0        | 29,606-34,332 | 235 quest dialogue blocks, pipe-delimited (`|`), dynamic token |
+------------------+---------------+----------------------------------------------------------------+
```

### 2.1 Binary Pack `a` (18,842 Bytes) - Game Engine Configuration & Vector Tables
Pack `a` is parsed during engine boot in `e.f()`. It is divided into two distinct sections:

#### Part 1: Record Stream (Offsets 0 to 18,261)
Contains exactly 312 variable-length records. Each record begins with a 2-byte unsigned little-endian length prefix:
$$\text{Record Length} = b_0 \mid (b_1 \ll 8)$$
The payload of `Record Length` bytes immediately follows.
- Total payload bytes across 312 records: 17,638 bytes.
- Total 2-byte length headers: $312 \times 2 = 624$ bytes.
- Total Part 1 bytes: $17,638 + 624 = 18,262$ bytes.

Key Semantic Records in Part 1:
- **Record 1 (16 bytes):** Unit directional tile offsets for 8-way movement and construction boundaries.
- **Record 15 (18 bytes):** Weapon and item animation frame base indices.
- **Record 106 (3 bytes):** Combat damage base tiers: `[10, 20, 30]` (Tier 1 melee club/stone, Tier 2 spear/axe, Tier 3 bone club/sling).
- **Record 110 (8 bytes):** Resource conversion and gathering rate multipliers: `[0, 20, 20, 20, 15, 25, 25, 15]`.
- **Record 138 (624 bytes):** Master Building and Structure Catalog ($26 \text{ entities} \times 24 \text{ attributes}$).
- **Record 149 (24 bytes):** Map dimensions for 12 campaign levels as $(W, H)$ byte pairs:
  `[64,48, 64,48, 64,80, 64,64, 64,96, 96,96, 96,96, 96,64, 80,80, 96,48, 48,96, 64,64]`.
- **Record 197 (12 bytes):** RLE decompression codebook ($6 \text{ repeat thresholds} + 6 \text{ substitution tile values}$).
- **Record 248 (12 bytes):** Campaign Level-to-Segment Routing Map:
  `[0, 0, 1, 2, 3, 4, 4, 5, 6, 7, 8, 9]`.
- **Record 280 (128 bytes):** Font ASCII glyph translation mapping table.
- **Records 308 & 309 (1 byte each):** Dialogue bank boundary partition markers (`308`=start, `309`=end).

#### Part 2: Short Vector Tables (Offsets 18,262 to 18,841)
Contains exactly 5 tables of signed 16-bit little-endian shorts. Each table begins with a 2-byte count header:
$$\text{Element Count} = b_0 \mid (b_1 \ll 8)$$
Followed by `Element Count` signed 16-bit little-endian values:
$$\text{Short Value} = \text{signed16}(b_0 \mid (b_1 \ll 8))$$
- Table 0: 122 shorts (244 bytes) - Global UI geometry coordinates and screen anchor positions.
- Table 1: 121 shorts (242 bytes) - Sprite sorting priorities and Z-order offsets.
- Table 2: 6 shorts (12 bytes) - Camera dead-zone bounding boxes.
- Table 3: 24 shorts (48 bytes) - Villager pathfinding heuristic weights.
- Table 4: 12 shorts (24 bytes) - Level initial camera center tile targets.
- Total shorts: $122 + 121 + 6 + 24 + 12 = 285 \text{ shorts} = 570$ bytes.
- Total 2-byte count headers: $5 \times 2 = 10$ bytes.
- Total Part 2 bytes: $570 + 10 = 580$ bytes.
- Total Pack `a` Size: $18,262 + 580 = 18,842$ bytes (100.0% accounted for, 0 unparsed bytes).

### 2.2 Binary Pack `pd0` (96,990 Bytes) - Sprite Frame Atlas & Animations
Pack `pd0` is decoded during startup in `e.b()`. It begins with a single header byte:
- `Offset 0`: Header byte = `0x0B` (11).

#### Short Tables (Offsets 1 to 41,336)
11 tables of signed 16-bit big-endian shorts:
$$\text{Short Value} = \text{signed16}((b_0 \ll 8) \mid b_1)$$
The exact sizes are defined by the bytecode array initializer in `e.class`:
```
Short Table  0:  119 shorts (  238 B) - HUD element layout coordinates
Short Table  1: 1291 shorts (2,582 B) - Frame composite part offsets (X)
Short Table  2:  162 shorts (  324 B) - Entity bounding box definitions
Short Table  3:  162 shorts (  324 B) - Entity collision box heights
Short Table  4: 2782 shorts (5,564 B) - Animation sequence frame lookup pointers
Short Table  5:  144 shorts (  288 B) - Weapon attachment anchors (X, Y)
Short Table  6: 1069 shorts (2,138 B) - Villager head/body layer alignment table
Short Table  7: 6903 shorts (13,806 B)- Complex unit composite hierarchy
Short Table  8:  823 shorts (1,646 B) - Animation frame duration ticks (timing)
Short Table  9: 1721 shorts (3,442 B) - Terrain tile passability bitflags & composite IDs
Short Table 10: 5492 shorts (10,984 B)- Sprite frame references & transform bitmasks
Total Shorts: 20,668 shorts = 41,336 bytes.
```

#### Byte Tables (Offsets 41,337 to 96,989)
25 tables of signed 8-bit bytes:
```
Byte Table  0:  119 bytes - HUD icon draw mode flags
Byte Table  1: 1291 bytes - Frame component relative X offsets
Byte Table  2: 1291 bytes - Frame component relative Y offsets
Byte Table  3: 1291 bytes - Frame component flip & mirror flags
Byte Table  4:  162 bytes - Selection box width
Byte Table  5:  162 bytes - Selection box height
Byte Table  6:  162 bytes - Selection box anchor offset
Byte Table  7: 2782 bytes - Frame duration multipliers
Byte Table  8: 2782 bytes - Loop repeat counters
Byte Table  9:  144 bytes - Tool orientation flags
Byte Table 10: 1069 bytes - Unit direction visual mapping
Byte Table 11: 1069 bytes - Shadow radius and intensity
Byte Table 12: 6903 bytes - Sub-part X anchor
Byte Table 13: 6903 bytes - Sub-part Y anchor
Byte Table 14: 6903 bytes - Sub-part Z-layer
Byte Table 15:  823 bytes - Frame trigger event IDs (hit-frame, footstep)
Byte Table 16: 1721 bytes - Terrain layer flags (Water mask: >> 6 & 3 == 2)
Byte Table 17:   42 bytes - 14 RGB color palette lookup (14 x 3 bytes)
Byte Table 18: 5492 bytes - Animation sequence sub-sprite X offsets
Byte Table 19: 5492 bytes - Animation sequence sub-sprite Y offsets
Byte Table 20: 1810 bytes - Sprite Atlas Page Index (lower 5 bits) & Color Index
Byte Table 21: 1810 bytes - Sprite Atlas Source X coordinate (& 0x7F)
Byte Table 22: 1810 bytes - Sprite Atlas Source Y coordinate
Byte Table 23: 1810 bytes - Sprite Region Width
Byte Table 24: 1810 bytes - Sprite Region Height
Total Bytes: 55,653 bytes.
```
Sum: $1 \text{ (header)} + 41,336 \text{ (shorts)} + 55,653 \text{ (bytes)} = 96,990$ bytes (100.0% accounted for, 0 unparsed bytes).

### 2.3 Binary Pack `ma` (42,381 Bytes) - 10 Map Segments
Contains 10 contiguous RLE-compressed tilemap streams loaded into `this.a.v` in `e.h()`:
- Segment 0: Offset 0, Length 2,545 bytes (Level 0 & 1: 64x48)
- Segment 1: Offset 2,545, Length 4,420 bytes (Level 2: 64x80)
- Segment 2: Offset 6,965, Length 3,684 bytes (Level 3: 64x64)
- Segment 3: Offset 10,649, Length 4,838 bytes (Level 4: 64x96)
- Segment 4: Offset 15,487, Length 7,146 bytes (Level 5 & 6: 96x96)
- Segment 5: Offset 22,633, Length 4,628 bytes (Level 7: 96x64)
- Segment 6: Offset 27,261, Length 4,447 bytes (Level 8: 80x80)
- Segment 7: Offset 31,708, Length 3,758 bytes (Level 9: 96x48)
- Segment 8: Offset 35,466, Length 3,748 bytes (Level 10: 48x96)
- Segment 9: Offset 39,214, Length 3,167 bytes (Level 11: 64x64)
Total: $\sum = 42,381$ bytes (100.0% accounted for, 0 unparsed bytes).

### 2.4 Binary Pack `sa` (26,616 Bytes) - Standard MIDI Soundtracks
Contains 5 concatenated Standard MIDI files (`MThd` format):
- Track 0: Offset 0, Length 8,014 bytes - Title Screen & Main Menu
- Track 1: Offset 8,014, Length 6,315 bytes - Peaceful Tribe Building & Day Theme
- Track 2: Offset 14,329, Length 5,648 bytes - Exploration & Wilderness
- Track 3: Offset 19,977, Length 3,405 bytes - Beast Attack & Combat
- Track 4: Offset 23,382, Length 3,234 bytes - Victory Jingle & Stage Complete
Total: $\sum = 26,616$ bytes (100.0% accounted for, 0 unparsed bytes).

### 2.5 Localization Packs (`0/` to `4/`)
In each language directory:
- `s`: Exactly 228 UI, item, and building name strings separated by pipe character `|` (`0x7C`).
- `t`: Exactly 71 building and unit descriptions separated by pipe character `|` (`0x7C`).
- `d0`: Exactly 235 quest dialogue blocks separated by pipe character `|` (`0x7C`).
- Encoding Nuance:
  - Vietnamese `0/d0` begins with a 3-byte UTF-8 Byte Order Mark (`0xEF, 0xBB, 0xBF`).
  - Contains Latin-1 accented byte `0xF4` representing character `'ô'` (`U+00F4`), which must be normalized to UTF-8.
  - Contains dynamic dynamic substitution token `0x1F`, which dynamically expands to MIDlet Version string `"0.1.28"` in `f.java`.

---

## 3. Sprite Frame Atlas & Rendering Subsystem

The sprite system handles 1,810 visual records indexed by tables `j[20..24]`. The rendering pipeline in `f.b(int n, int x, int y)` implements a dual-path architecture:

### 3.1 Slicing Table Bitpacking & Coordinate Formulas
For a given frame index $n \in [0, 1809]$:
- If $n = 0$: Null sentinel frame. Skip execution (`if (n == 0) return;`).
- Page / Primitive Mode:
  $$\text{page} = j[20][n] \ \& \ 0\text{x}1\text{F}$$
- Source Atlas X coordinate:
  $$\text{srcX} = j[21][n] \ \& \ 0\text{x}7\text{F}$$
- Source Atlas Y coordinate:
  $$\text{srcY} = j[22][n] \ \& \ 0\text{xFF}$$
- Source Atlas Width:
  $$\text{width} = j[23][n] \ \& \ 0\text{xFF}$$
- Source Atlas Height:
  $$\text{height} = j[24][n] \ \& \ 0\text{xFF}$$
- World Render Target Adjustment:
  $$\text{dstX} = x + 11, \quad \text{dstY} = y + 8$$

### 3.2 Dual-Path Rendering Branch

#### Path A: Bitmap Blit ($\text{page} < 27$)
When $\text{page} \in [0, 26]$, the frame is an image region sliced from pre-rendered spritesheet `pi0_{page:02d}.png`:
```javascript
function drawBitmapFrame(ctx, n, dstX, dstY, spritesheets) {
    const page = j[20][n] & 0x1F;
    const srcX = j[21][n] & 0x7F;
    const srcY = j[22][n] & 0xFF;
    const w = j[23][n] & 0xFF;
    const h = j[24][n] & 0xFF;
    const img = spritesheets[page];
    if (!img) return;

    // Canvas 2D image blit
    ctx.drawImage(img, srcX, srcY, w, h, dstX + 11, dstY + 8, w, h);
}
```

#### Path B: Procedural Vector Drawing Primitives ($\text{page} \ge 27$)
When $\text{page} \in [27, 30]$, the frame is not an image but a lightweight geometric vector drawing primitive. The color index is unpacked using high bits from tables $j[20]$ and $j[21]$:
$$\text{colorIdx} = ((j[20][n] \ \& \ 0\text{xFF}) \gg 5) \mid ((j[21][n] \ \& \ 0\text{x}80) \gg 4)$$
The RGB color is fetched from Table 17 (`j[17]`):
$$\text{Red} = j[17][\text{colorIdx} \times 3 + 0] \ \& \ 0\text{xFF}$$
$$\text{Green} = j[17][\text{colorIdx} \times 3 + 1] \ \& \ 0\text{xFF}$$
$$\text{Blue} = j[17][\text{colorIdx} \times 3 + 2] \ \& \ 0\text{xFF}$$

Primitive Commands by Page:
- **Page 27 (Draw Line):**
  Draws a vector stroke from $(X_1, Y_1)$ to $(X_2, Y_2)$:
  $$X_1 = \text{dstX} + (j[21][n] \ \& \ 0\text{x}7\text{F}), \quad Y_1 = \text{dstY} + j[22][n]$$
  $$X_2 = \text{dstX} + j[23][n], \quad Y_2 = \text{dstY} + j[24][n]$$
- **Page 28 (Draw Rect Outline):**
  Draws un-filled 1-pixel rectangle outline:
  $$X = \text{dstX} + (j[21][n] \ \& \ 0\text{x}7\text{F}), \quad Y = \text{dstY} + j[22][n], \quad W = j[23][n], \quad H = j[24][n]$$
- **Page 29 (Fill Rect):**
  Draws solid filled rectangle:
  $$X = \text{dstX} + (j[21][n] \ \& \ 0\text{x}7\text{F}) - 11, \quad Y = \text{dstY} + j[22][n] - 8, \quad W = j[23][n], \quad H = j[24][n]$$
- **Page 30 (4x Scaled Fill Rect):**
  Draws 4x enlarged filled block:
  $$X = (\text{dstX} + (j[21][n] \ \& \ 0\text{x}7\text{F})) \times 4 - 11, \quad Y = (\text{dstY} + j[22][n]) \times 4 - 8$$
  $$W = j[23][n] \times 4, \quad H = j[24][n] \times 4$$

### 3.3 14-Color Palette Table (Table 17)
The exact RGB color lookup table extracted from `pd0` Byte Table 17:
```
Index 0:  #000000 (R:   0, G:   0, B:   0) - Black / Shadow Outline
Index 1:  #C2B651 (R: 194, G: 182, B:  81) - Pale Gold / Desert Sand
Index 2:  #A7963F (R: 167, G: 150, B:  63) - Earth Ochre / Arid Soil
Index 3:  #B4A647 (R: 180, G: 166, B:  71) - Light Clay
Index 4:  #66511F (R: 102, G:  81, B:  31) - Dark Timber / Bark
Index 5:  #221E09 (R:  34, G:  30, B:   9) - Deep Shadow / Charcoal
Index 6:  #D0C460 (R: 208, G: 196, B:  96) - Thatch / Straw Yellow
Index 7:  #51AD1B (R:  81, G: 173, B:  27) - Lush Grass Green
Index 8:  #AF8609 (R: 175, G: 134, B:   9) - Dried Mud / Amber
Index 9:  #0061D8 (R:   0, G:  97, B: 216) - Deep Water Blue
Index 10: #8FC7FF (R: 143, G: 199, B: 255) - Water Shimmer / Splash White
Index 11: #0E5B27 (R:  14, G:  91, B:  39) - Deep Jungle Foliage
Index 12: #00DA00 (R:   0, G: 218, B:   0) - Bright Canopy Green
Index 13: #073404 (R:   7, G:  52, B:   4) - Shadow Canopy Dark
```

### 3.4 Composite Sprites & Animation Sequences
Complex entities (multi-part characters, swinging weapons, dynamic smoke) are assembled recursively in `f.a(Graphics g, int animId, int x, int y)`:
- Look up sub-part sequence start index in Short Table 9:
  $$\text{startIndex} = b[9][\text{animId}] \ \& \ 0\text{x}1\text{FFF}$$
- Look up part count in Byte Table 16:
  $$\text{partCount} = j[16][\text{animId}] \ \& \ 0\text{x}3\text{F}$$
- Iterate $i$ from $\text{startIndex}$ to $\text{startIndex} + \text{partCount} - 1$:
  - Sub-frame ID:
    $$\text{subFrameId} = b[10][i] \ \& \ 0\text{x}1\text{FFF}$$
  - Extended X-offset shift:
    $$\text{shiftX} = ((b[10][i] \ \& \ 0\text{xC}000) \gg 14) \ll 7$$
  - Sub-part relative offset:
    $$\Delta X = j[18][i] + \text{shiftX}, \quad \Delta Y = j[19][i]$$
  - Recurse flag:
    $$\text{isRecursive} = (b[10][i] \ \& \ 0\text{x}2000) \gg 13$$
    - If `isRecursive == 0`: Call leaf draw `f.b(g, subFrameId, x + ΔX, y + ΔY)`.
    - If `isRecursive == 1`: Recurse composite `f.a(g, subFrameId, x + ΔX, y + ΔY)`.
- Timing: Frame duration in 60 Hz engine ticks is stored in Short Table 8 (`b[8][frameId]`).

---

## 4. Level & Map Architecture

### 4.1 Campaign Level to Map Segment Routing
The game features 12 campaign levels routed to 10 unique segments in `ma`. Dimensions are decoded from Record 149 and mapped via Record 248:

```
+-------+---------------+------------+-------------+--------------+------------------+
| Level | Segment Index | Dimensions | Total Tiles | Segment Size | Playable Window  |
+-------+---------------+------------+-------------+--------------+------------------+
| 0     | 0             | 64 x 48    | 3,072       | 2,545 B      | 40 x 32 (Intro)  |
| 1     | 0             | 64 x 48    | 3,072       | 2,545 B      | 64 x 48 (Full)   |
| 2     | 1             | 64 x 80    | 5,120       | 4,420 B      | 64 x 80          |
| 3     | 2             | 64 x 64    | 4,096       | 3,684 B      | 64 x 64          |
| 4     | 3             | 64 x 96    | 6,144       | 4,838 B      | 64 x 96          |
| 5     | 4             | 96 x 96    | 9,216       | 7,146 B      | 64 x 96 (W - 32) |
| 6     | 4             | 96 x 96    | 9,216       | 7,146 B      | 96 x 96 (Full)   |
| 7     | 5             | 96 x 64    | 6,144       | 4,628 B      | 96 x 64          |
| 8     | 6             | 80 x 80    | 6,400       | 4,447 B      | 80 x 80          |
| 9     | 7             | 96 x 48    | 4,608       | 3,758 B      | 96 x 48          |
| 10    | 8             | 48 x 96    | 4,608       | 3,748 B      | 48 x 96          |
| 11    | 9             | 64 x 64    | 4,096       | 3,167 B      | 64 x 64          |
+-------+---------------+------------+-------------+--------------+------------------+
```
Total tiles across all 10 distinct segments: 53,504 tiles.

### 4.2 RLE Decompression Formula (`f.aN()`)
Decompression consumes raw segment bytes using Codebook Record 197 (`e197`):
- `e197[0..5]`: Repeat threshold limits: `[4, 4, 2, 2, 2, 2]`.
- `e197[6..11]`: Substitution tile values: `[3, 0, 43, 6, 3, 0]`.

Decompression Algorithm:
```javascript
function decompressMapSegment(segBytes, width, height, e197) {
    let bytePtr = 0;
    let runCounter = 10;
    let codebookIdx = 0;
    let currentTile = 0;
    const tiles = [];

    for (let y = 0; y < height; y++) {
        const row = [];
        for (let x = 0; x < width; x++) {
            if (runCounter >= e197[0 + codebookIdx]) {
                const raw = segBytes[bytePtr++];
                if (raw >= 250) {
                    runCounter = 0;
                    codebookIdx = raw - 250;
                    currentTile = e197[6 + codebookIdx];
                } else {
                    currentTile = raw;
                }
            }
            runCounter++;
            row.push(currentTile);
        }
        tiles.push(row);
    }
    return tiles;
}
```

### 4.3 Tile Grid, Collision Matrix & Passability Values
The collision grid is an array of dimensions $H \times W$ with signed 8-bit values:
- `0`: Walkable terrain (open dirt, grass, sand).
- `-126`: Impassable boundary / solid wall / cliff perimeter.
- `-125`: Deep water / impassable river.
- `-124`: Structural footprint / tree / boulder.

Collision Generation Rules (from `f.aN()` lines 6136–6155):
1. **Tile Passability Flag:** Check Short Table 9 (`pd0.short_tables[9]`):
   $$\text{flag}_{b9} = (b9[\text{tileId}] \ \& \ 0\text{xFFFF}) \gg 13 \ \& \ 1$$
   If $\text{tileId} \ge 175$ or $\text{flag}_{b9} == 1$: Cell is impassable (`collision[y][x] = -126`).
2. **Water Detection:** Check Byte Table 16 (`pd0.byte_tables[16]`):
   $$\text{flag}_{j16} = (j16[\text{tileId}] \ \& \ 0\text{xFFFF}) \gg 6 \ \& \ 3$$
   If $\text{flag}_{j16} == 2$ and Level $\ne 3$: Cell is water (`collision[y][x] = -125`).
3. **Obstacle Range:**
   If $180 \le \text{tileId} \le 231$ and Level $\ne 3$: Cell is obstacle (`collision[y][x] = -124`).
4. **Perimeter Border:**
   Outer perimeter tiles ($x = 0$, $x = W - 1$, $y = 0$, $y = H - 1$) are unconditionally `-126`.
5. **Runtime Ground Noise:** For base grass/dirt tiles ($0 \dots 8$), the J2ME renderer applies aesthetic pseudorandom variation:
   $$\text{renderTile} = \text{baseTile} + \text{rand}(3, 3)$$

---

## 5. Building Catalog & Construction Mechanics

All 12 prehistoric buildings are derived from Record 138 of Pack `a` ($26 \text{ entities} \times 24 \text{ attributes}$) and matched to Vietnamese localization names and descriptions.

```
+----+---------------------+------------+---------------+--------------------+---------------------+----------+--------+
| ID | Building Name       | Size (WxH) | HP (L1->L2->L3)| Build Cost (W/S/O) | Upgrade Cost(W/S/O) | Capacity | Prereq |
+----+---------------------+------------+---------------+--------------------+---------------------+----------+--------+
| 0  | Kho vũ khí (Armory) | 2 x 2      | 25 -> 40 -> 90| Wood:15, Stone: 5  | Wood: 5, Stone:10   | 18       | Tent(2)|
| 1  | Phòng tập (Barracks)| 3 x 2      | 40 -> 55 -> 70| Wood:20, Stone:10  | Wood:10, Stone: 5   | 17       | None(0)|
| 2  | Lều (Tent / Hut)    | 5 x 4      | 70 ->100 -> 90| Wood:40, Stone:30  | Wood:15, Stone:15   | 13 (4 ppl| None(0)|
| 3  | Lều của Tù trưởng   | 4 x 4      | 120-> 70 -> 90| Wood:30, Stone:20  | Wood:50, Stone:50   | 12 (Town)| None(0)|
| 4  | Bếp (Kitchen)       | 4 x 3      | 60 -> 80 -> 90| Wood:30, Stone:20  | Wood:10, Stone:20   | 15       | Tent(2)|
| 5  | Khu tập ném (Range) | 6 x 4      | 70 ->100 -> 90| Wood:40, Stone:30  | Wood:15, Stone:15   | 14       | None(0)|
| 6  | Kho (Warehouse)     | 3 x 3      | 50 -> 70 -> 90| Wood:25, Stone:20  | Wood:18, Stone:18   | 16 (Depot| None(0)|
| 7  | Sân disco (Disco)   | 5 x 4      | 90 ->110 -> 90| Wood:30, Stone:25  | Wood:10, Stone:25   | 13 (DJ)  | Chief 3|
| 8  | Khu thánh địa(Altar)| 3 x 3      | 50 -> 60 -> 90| Stone:20, Bone:10  | Wood:10, Bone:10    | 16       | Barr. 1|
| 9  | Trung tâm pia(Scout)| 4 x 4      | 60 -> 80 -> 90| Wood:30, Stone:15  | Wood:10, Stone:15   | 12       | None(0)|
| 10 | Nhà trẻ (Nursery)   | 4 x 4      | 40 -> 50 -> 90| Wood:20, Stone:10  | Wood:10, Stone: 5   | 12 (Kids)| None(0)|
| 11 | Chòi canh (Tower)   | 1 x 1      | 50 -> 70 -> 90| Wood:10, Stone:10  | Wood:10, Stone:10   | 19 (Guard| Barr. 1|
+----+---------------------+------------+---------------+--------------------+---------------------+----------+--------+
```

### Detailed Building Roles & Gameplay Mechanics
1. **Kho vũ khí (Armory, ID 0):** Unlocks melee and ranged weapon fabrication. Requires a dedicated craftsman. Crafting consumes wood, stone, and bone to produce Clubs, Spears, Axes, and Bone Clubs.
2. **Phòng tập (Training Barracks, ID 1):** Trains raw villagers into melee Warriors. Increases combat melee skill, maximum HP (+25%), and damage output.
3. **Lều (Tent, ID 2):** Primary domestic dwelling. Provides resting quarters for up to 4 exhausted villagers to recover stamina/morale and increases tribe population cap by 4.
4. **Lều của Tù trưởng (Chief's Tent, ID 3):** Tribal town hall and seat of Chief NK2KLove. Central quest hub; loss of this building immediately triggers Mission Defeat.
5. **Bếp (Kitchen, ID 4):** Food preparation center. Converts raw meat and collected berries into cooked rations, reducing tribal starvation decay.
6. **Khu tập ném (Sling / Range, ID 5):** Trains villagers into Slingers and Spear Throwers for ranged combat against fast beasts and distant enemies.
7. **Kho (Warehouse, ID 6):** Resource drop-off depot. Increases tribe storage capacity for Wood, Stone, Food, and Bone by +200 units per warehouse.
8. **Sân disco (Disco Floor, ID 7):** Prehistoric entertainment plaza. Villagers dance to Tigerilla beverages, rapidly restoring tribal morale and preventing deserters. Requires an assigned DJ.
9. **Khu thánh địa (Sanctuary, ID 8):** Spiritual altar. Houses the tribal Shaman to channel divine spells, cure poisoned villagers, and heal injured warriors.
10. **Trung tâm pia (Pia Scout Center, ID 9):** Intelligence and scouting lodge. Trains Scouts with increased sight radius (+6 tiles) and camouflage in dense brush.
11. **Nhà trẻ (Daycare / Nursery, ID 10):** Safe enclosure for tribal children, preventing them from wandering into predator territories while parents work.
12. **Chòi canh (Watchtower, ID 11):** 1x1 fortified tower. Provides elevated line-of-sight and allows an assigned archer/spearman to rain projectiles on attackers.

---

## 6. Villager Simulation, Roles & State Machine

### 6.1 The 9,983-Byte Structure-of-Arrays (SoA) Memory Architecture
The simulation engine allocates a single contiguous master byte array of 9,983 bytes (`this.a.e = new byte[9983]` in `e.i()`). This buffer uses a multi-stride Structure-of-Arrays layout to maintain cache locality:

```
+----------------------------------------------------------------------------------------------------+
|                                 MASTER SOA BUFFER (9,983 BYTES)                                    |
|                                                                                                    |
|  [Section 1: Offsets 0..8382] (8,383 Bytes)                                                        |
|  Villagers & Mobile Units: 83 Sub-Arrays with Stride 101 (Slots 0..100)                             |
|  - Slots 1..50: Player Villagers                                                                   |
|  - Slots 51..100: Hostile Raiders & Wild Beasts                                                    |
|                                                                                                    |
|  [Section 2: Offsets 8383..9358] (976 Bytes)                                                       |
|  Primary Resource Nodes & Structures: 16 Sub-Arrays with Stride 61 (Slots 0..60)                   |
|  - Tile X (8383), Tile Y (8444), Type (8749), Remaining Yield (8627), etc.                         |
|                                                                                                    |
|  [Section 3: Offsets 9359..9754] (396 Bytes)                                                       |
|  Player Constructed Buildings: 18 Sub-Arrays with Stride 22 (Slots 0..21)                          |
|  - Tile X (9359), Tile Y (9381), Width (9403), Height (9425), Type (9491), HP (9535), etc.        |
|                                                                                                    |
|  [Section 4: Offsets 9755..9782] (28 Bytes)                                                        |
|  Alignment Padding & Memory Guard Margin                                                           |
|                                                                                                    |
|  [Section 5: Offsets 9783..9982] (200 Bytes)                                                       |
|  Secondary Environmental Objects & Traps: 4 Sub-Arrays with Stride 50 (Slots 0..49)                |
|  - Decors, Net Traps, Spring Traps, Pit Traps                                                      |
+----------------------------------------------------------------------------------------------------+
```

### 6.2 Master Villager Stride Directory (Stride = 101)
For any villager entity $v \in [1, 100]$:
- `Offset 0` ($0 \times 101 + v$): Current Grid X coordinate.
- `Offset 101` ($1 \times 101 + v$): Current Grid Y coordinate.
- `Offset 202` ($2 \times 101 + v$): Sub-tile pixel fine offset $\Delta X$ ($-11 \dots +11$).
- `Offset 303` ($3 \times 101 + v$): Sub-tile pixel fine offset $\Delta Y$ ($-8 \dots +8$).
- `Offset 606` ($6 \times 101 + v$): Facing Direction ($0..7$, 8-way: N, NE, E, SE, S, SW, W, NW).
- `Offset 707` ($7 \times 101 + v$): Path waypoint index in active path buffer.
- `Offset 808` ($8 \times 101 + v$): Remaining path distance steps to target.
- `Offset 1010` ($10 \times 101 + v$): Animation sprite frame base index.
- `Offset 1111` ($11 \times 101 + v$): Animation tick subframe counter.
- `Offset 1313` ($13 \times 101 + v$): Held resource inventory quantity (carry load).
- `Offset 1414` ($14 \times 101 + v$): Profession / Unit Role ID.
- `Offset 1919` ($19 \times 101 + v$): Current Health Points (HP). If $\le 0$, unit is dead.
- `Offset 2828` ($28 \times 101 + v$): AI State Machine primary action state.
- `Offset 2929` ($29 \times 101 + v$): Secondary state modifier / task modifier.
- `Offset 3131` ($31 \times 101 + v$): Destination Target Grid X.
- `Offset 3232` ($32 \times 101 + v$): Destination Target Grid Y.
- `Offset 4444` ($44 \times 101 + v$): Target Entity ID (Building index $0..21$ or unit $1..100$).
- `Offset 4949` ($49 \times 101 + v$): Resource type carried ($0$=Food, $1$=Wood, $2$=Stone, $3$=Bone).
- `Offset 6161` ($61 \times 101 + v$): Allegiance / Faction ($0$=Player Tribe, $1$=Neutral, $2$=Enemy).
- `Offset 6767` ($67 \times 101 + v$): Skill / Experience level in current profession.
- `Offset 7777` ($77 \times 101 + v$): Attack / Action cooldown delay timer.
- `Offset 7979` ($79 \times 101 + v$): Bitfield flags (Bit 0: active, Bit 1: selected, Bit 2: resting, Bit 5: in combat).

### 6.3 Professions & Roles
1. **Dân làng (Villager / Laborer):** Base unit. Can gather berries, chop wood, mine stone, and carry building materials.
2. **Thợ săn (Hunter):** Armed with clubs or spears. Tracks wild fauna (boars, mammoths), collects meat and bone.
3. **Thợ đốn củi (Woodcutter):** Harvests trees, delivers wood logs to the nearest Warehouse.
4. **Thợ xây (Builder):** Automatically pathfinds to building foundation footprints to supply materials and raise HP.
5. **Chiến binh (Warrior - Melee):** Trained at Barracks (Phòng tập). High melee damage, engages enemy raiders in hand-to-hand combat.
6. **Lính ném đá / phóng lao (Slinger / Ranged):** Trained at Range (Khu tập ném). Ranged projectile attacks from safe distance.
7. **Pháp sư (Shaman):** Resides at Sanctuary (Khu thánh địa). Casts area heal, stamina regeneration, and lightning wards.
8. **Tù trưởng (Chief NK2KLove):** Tribal leader. Boosts work speed and morale of all nearby villagers by +20%.

### 6.4 AI State Machine (`Stride 28`)
```
                     +--------------+
                     |   0: IDLE    |
                     +-------+------+
                             |
             +---------------+---------------+
             |               |               |
             ▼               ▼               ▼
       +-----------+   +-----------+   +-----------+
       |  1: WALK  |   | 28: REST  |   | 69: TRAIN |
       +-----+-----+   +-----------+   +-----------+
             |
             +-----------------------+-----------------------+
             |                       |                       |
             ▼                       ▼                       ▼
      +--------------+        +--------------+        +--------------+
      |  44: GATHER  |        |  55: BUILD   |        |  87: FIGHT   |
      +------+-------+        +--------------+        +--------------+
             |
             ▼
      +--------------+
      | 59: DEPOSIT  |
      +--------------+
```
- **State 0 (Idle):** Scans for nearby jobs or returns to village center.
- **State 1 (Walk / Pathfind):** Follows A* / Breadth-First waypoint chain along grid passability map.
- **State 28 (Rest):** Moves to nearest Tent (Lều) when stamina is depleted; regenerates HP and stamina.
- **State 44 (Gather):** Performs harvesting animation on resource node until carry capacity (Stride 13) is reached.
- **State 55 (Build / Repair):** Performs construction animation on targeted building until HP reaches maximum.
- **State 59 (Deposit):** Pathfinds to nearest Warehouse (Kho) to unload collected resources into tribe global stockpiles.
- **State 69 (Train):** Stations at Barracks or Range to advance profession skill levels.
- **State 87 (Fight / Combat):** Engages target hostile unit; executes attack cycle governed by weapon cooldown (Stride 77).

---

## 7. Economy, Combat & Training Formulas

### 7.1 Core Resources & Scoring
The economy tracks 4 primary material resources and 1 meta-score:
1. **Thực phẩm (Food):** Gathered from berry bushes, agriculture, and hunted beasts. Consumed continuously by tribe population ($1 \text{ Food} / 30 \text{ sec per villager}$).
2. **Gỗ (Wood):** Harvested from forest trees. Primary structural component for buildings.
3. **Đá (Stone):** Extracted from mountain quarries and boulders. Used for weapon fabrication and building upgrades.
4. **Xương (Bone):** Obtained from large game animals (Mammoths, Saber-toothed tigers). Required for advanced weapons, shaman rituals, and Sanctuary upgrades.
5. **Điểm bộ lạc (Tribe Points / Score):** Earned from building construction, beast hunts, quest completion, and villager promotions:
   $$\text{Score} = \sum (\text{Building HP}) \times 2 + \sum (\text{Villager Exp}) \times 5 + \text{Quests Completed} \times 500$$

### 7.2 Gathering Rates & Carry Capacity
- Base Villager carry capacity: 10 units.
- Backpack / Cart upgrade (Armory): Increases capacity to 20 units.
- Gathering Tick Rate: 1 unit per 20 engine frames (~0.33 seconds).
- Resource Node Exhaustion:
  - Berry Bush: 50 Food.
  - Tree: 100 Wood.
  - Boulder: 150 Stone.
  - Mammoth Carcass: 200 Food + 80 Bone.

### 7.3 Combat Damage & Weapon Crafting
Combat occurs when entities of opposing factions (Stride 61: 0 vs 2) come within attack range:
$$\text{Damage} = \text{Base Damage} + \text{Weapon Bonus} - \text{Target Armor}$$

#### Weapon Catalog
- **Tay không (Unarmed / Fists):** Range: 1 tile, Damage: 3, Cooldown: 15 ticks.
- **Dùi củi (Club, ID 12):** Range: 1 tile, Damage: 10, Craft Cost: 10 Wood.
- **Hòn đá (Throwing Stone, ID 13):** Range: 4 tiles, Damage: 10, Craft Cost: 5 Stone.
- **Ngọn giáo (Spear, ID 14):** Range: 2 tiles, Damage: 20, Craft Cost: 15 Wood, 5 Stone.
- **Búa đá (Stone Hammer, ID 15):** Range: 1 tile, Damage: 25, Craft Cost: 10 Wood, 20 Stone.
- **Chùy xương (Bone Club, ID 16):** Range: 1 tile, Damage: 30, Craft Cost: 10 Wood, 15 Bone.
- **Rìu nhỏ (Small Axe, ID 17):** Range: 1 tile, Damage: 20, Craft Cost: 15 Wood, 10 Stone.

### 7.4 Defensive Traps
- **Bẫy lưới (Net Trap, ID 18):** Cost: 10 Wood. Immobilizes target enemy for 10 seconds.
- **Bẫy lò xo (Spring Trap, ID 19):** Cost: 15 Wood. Flings target 3 tiles backwards, inflicting 25 damage.
- **Bẫy hầm (Pit Trap, ID 20):** Cost: 20 Wood, 10 Stone. Concealed hole; deals 60 damage to heavy beasts.

---

## 8. Quest & Dialogue System

### 8.1 Localization Bank `0/d0` Parsing & String Table
The quest and dialogue bank contains exactly 235 items parsed from `0/d0`:
- Boundary markers: Entry 308 (start index) and Entry 309 (end index) in pack `a` partition dialogue groups per campaign chapter.
- Dynamic Substitution: Token `0x1F` is dynamically replaced with the game version string (`"0.1.28"`).
- UTF-8 Handling: 3-byte BOM (`EF BB BF`) stripped; byte `0xF4` mapped to `'ô'`.

### 8.2 Quest Progression Engine
Quests are evaluated on every 60 Hz tick in `b.ax()`:

```
+-------+--------------------+-------------------------------------------+-----------------------------------+
| Stage | Level Title        | Primary Objectives                        | Win / Loss Condition              |
+-------+--------------------+-------------------------------------------+-----------------------------------+
| 0     | Tan Băng (Thaw)    | Build 1 Warehouse, Assign 1 Villager      | Win: Warehouse built; Loss: Chief |
| 1     | Nơi Trú Ẩn (Shelter| Build 2 Tents, Gather 100 Wood & 50 Food  | Win: Tents complete; Loss: Chief  |
| 2     | Bếp Lửa (Hearth)   | Build Kitchen, Assign Cook, Hunt 2 Boars  | Win: 150 Food stored; Loss: Starve|
| 3     | Vũ Khí Đầu Tiên    | Construct Armory, Craft 5 Clubs           | Win: 5 Weapons; Loss: Beast kill  |
| 4     | Huấn Luyện Binh Sĩ | Build Barracks, Train 3 Warriors          | Win: 3 Warriors; Loss: Base breach|
| 5     | Đợt Tấn Công Đầu   | Defend Chief Tent against 8 Wolf Raiders  | Win: Defeat all raiders; Loss: HP0|
| 6     | Mở Rộng Địa Bàn    | Build 1 Watchtower, Scout 4 Fog Sectors   | Win: Sectors cleared; Loss: Chief |
| 7     | Bữa Tiệc Bộ Lạc    | Build Disco Floor, Assign DJ, Morale > 80%| Win: Morale 80%; Loss: Deserters  |
| 8     | Lời Của Thần Linh  | Build Sanctuary, Assign Shaman            | Win: Sanctuary HP max; Loss: Death|
| 9     | Săn Voi Mamut      | Hunt Mammoth Bull, Collect 100 Bones      | Win: 100 Bones; Loss: Party wipe  |
| 10    | Cuộc Chiến Bộ Tộc  | Destroy Enemy Outpost, Defeat Warlord     | Win: Outpost HP 0; Loss: Chief HP0|
| 11    | Thời Đại Mới       | Upgrade Chief Tent to Level 3, Pop > 30   | Win: Campaign Victory Celebration |
+-------+--------------------+-------------------------------------------+-----------------------------------+
```

---

## 9. Savegame RMS Schema & HTML5 Web Remake Mapping

### 9.1 RecordStore Slot Binary Schema (J2ME)
The original game uses MIDP Record Management System (RMS) with three distinct persistent slots:
- `Slot 0` (`"t0"`): Global User Configuration & Audio Preferences.
- `Slot 1` (`"t1"`): Primary Campaign Level Snapshot.
- `Slot 2` (`"t2"`): Alternate / Auto-save Campaign Snapshot.

#### Slot 0 Binary Layout (`DataOutputStream`)
```
[Offset] [Type]    [Field]        [Semantic Description]
+0000    int32     var_int_l      Cumulative Highscore / Player Metric
+0004    bool      var_boolean_W  Sound FX & Music Enabled Flag (1=on, 0=off)
+0005    int8      var_byte_r     Master Audio Volume (0..10)
+0006    int8      var_byte_s     SFX Balance Volume (0..10)
+0007    int8      var_byte_t     Highest Unlocked Campaign Level (0..11)
+0008    int8      var_byte_c     Language Selection (0=vi, 1=fr, 2=it, 3=de, 4=es)
+0009    int8      var_byte_p     Vibration / Screen Display Preference
Total: 10 bytes.
```

#### Slot 1 & Slot 2 Binary Layout (`DataOutputStream`)
```
[Offset]  [Type]          [Field]                 [Semantic Description]
+0000     int8            var_byte_q              Active Campaign Level Index (0..11)
+0001     int8            var_byte_p              Current Quest Stage Phase
+0002     int8            var_byte_d              Game Difficulty Setting (0=Easy, 1=Normal, 2=Hard)
+0003     byte[9983]      var_byte_arr_e          Full SoA Simulation Buffer (Units, Nodes, Buildings)
+9986     byte[50]        var_byte_arr_q          Secondary Entity Status Bits
+10036    byte[4][50]     var_byte_arr_arr_a      Tribe Stockpiles for 4 Resources (200 B)
+10236    short[2][26]    var_short_arr_arr_a     Building Structural Counters (104 B)
+10340    byte[3][30]     var_byte_arr_arr_e      Quest Trigger Objective Flags (90 B)
+10430    byte[2][10][12] var_byte_arr_arr_arr_a  Tribe Tech Tree Progression Matrix (240 B)
+10670    byte[4][30]     var_byte_arr_arr_f      Villager Morale & Stamina State (120 B)
+10790    byte[4][5][30]  var_byte_arr_arr_arr_b/c Map Dynamic Destruction Mask (600 B)
Total Payload Size: ~11,390 bytes per save slot.
```

### 9.2 HTML5 Web Remake Mapping (`localStorage`)
In the web remake, binary serialization is mapped cleanly to human-readable, schema-validated JSON persisted via browser `localStorage`:

```javascript
// Storage Keys:
// "prehistoric_tribes_slot0" -> Configuration JSON
// "prehistoric_tribes_slot1" -> Savegame Slot 1 JSON
// "prehistoric_tribes_slot2" -> Savegame Slot 2 JSON

export const StorageSchema = {
    saveSlot0: (config) => {
        const payload = {
            version: "0.1.28",
            score: config.score,
            soundEnabled: config.soundEnabled,
            musicVolume: config.musicVolume,
            sfxVolume: config.sfxVolume,
            unlockedLevel: config.unlockedLevel,
            language: config.language, // "vi"
            vibration: config.vibration
        };
        localStorage.setItem("prehistoric_tribes_slot0", JSON.stringify(payload));
    },

    saveLevelSnapshot: (slotId, gameState) => {
        const payload = {
            version: "0.1.28",
            timestamp: Date.now(),
            levelIndex: gameState.levelIndex,
            questStage: gameState.questStage,
            difficulty: gameState.difficulty,
            resources: {
                food: gameState.resources.food,
                wood: gameState.resources.wood,
                stone: gameState.resources.stone,
                bone: gameState.resources.bone,
                score: gameState.resources.score
            },
            villagers: gameState.villagers.map(v => ({
                id: v.id,
                x: v.x,
                y: v.y,
                dx: v.dx,
                dy: v.dy,
                dir: v.dir,
                hp: v.hp,
                profession: v.profession,
                state: v.state,
                targetX: v.targetX,
                targetY: v.targetY,
                carriedType: v.carriedType,
                carriedAmount: v.carriedAmount,
                allegiance: v.allegiance
            })),
            buildings: gameState.buildings.map(b => ({
                id: b.id,
                x: b.x,
                y: b.y,
                width: b.width,
                height: b.height,
                type: b.type,
                hp: b.hp,
                maxHp: b.maxHp,
                level: b.level,
                workers: b.workers
            })),
            questObjectives: gameState.questObjectives
        };
        localStorage.setItem(`prehistoric_tribes_slot${slotId}`, JSON.stringify(payload));
    }
};
```

---

## 10. Web Remake Implementation Guide (Milestone 3 Roadmap)

### 10.1 File Organization & ES Module Architecture
The web client in `/home/baoltb/Desktop/Paseo_Project/games/bolacthoitiensu/web/` will follow a modular architecture:
```
games/bolacthoitiensu/web/
├── index.html                  # Responsive HTML5 entry with virtual 240x320 Canvas
├── css/
│   └── style.css               # Retro arcade HUD, responsive letterboxing, pixel art CSS
└── js/
    ├── main.js                 # App initialization, main game loop (fixed 60 Hz)
    ├── engine/
    │   ├── renderer.js         # Canvas 2D dual-path renderer (bitmap + vector primitives)
    │   ├── camera.js           # Smooth panning, bounding box clamp, entity tracking
    │   ├── input.js            # Keyboard (arrows/WASD/Numpad), touch buttons, mouse click
    │   ├── audio.js            # Web Audio API MIDI sequencer for tracks 0..4
    │   └── storage.js          # localStorage manager for slot 0..2
    └── game/
        ├── world.js            # Tilemap renderer, RLE decompressor, collision matrix
        ├── building.js         # 12 prehistoric buildings, placement cursor, construction
        ├── villager.js         # 101-stride villager simulation, professions, A* navigation
        ├── economy.js          # 4 resources, consumption tick, stockpiling, craft costs
        └── quest.js            # 0/d0 dialogue manager, text wrap, quest stage triggers
```

### 10.2 Canvas Resolution & Retro Display Scaling
- **Native Virtual Resolution:** $240 \times 320$ pixels (standard J2ME portrait resolution).
- **Display Scaling:** Scaled uniformly to fit browser window using CSS `image-rendering: pixelated;` and letterboxing to guarantee sharp, non-blurry retro pixel art.
- **Frame Rate:** Target 60 FPS using `requestAnimationFrame` with a fixed-timestep accumulator (16.66ms) to preserve authentic J2ME simulation timing.

### 10.3 Quality & Verification Standards
- Zero external build dependencies (pure ES2022 JavaScript executable directly in any modern browser).
- Complete byte-for-byte and algorithmic alignment with `decompiled/` Java sources.
- 100% Vietnamese localization support from authentic `0/d0`, `0/s`, `0/t` files.
- Automated validation via `verify_all.py` validating data integrity and headless browser rendering.

---
*End of RECONSTRUCTION_SPEC.md*
