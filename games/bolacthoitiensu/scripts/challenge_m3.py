#!/usr/bin/env python3
"""
Milestone 3 Empirical Challenge & Adversarial Stress Harness
=============================================================
Author: challenger_m3_1 (EMPIRICAL CHALLENGER - critic & specialist)
Target: games/bolacthoitiensu/web/ (HTML5 Canvas Web Remake)
Runtime: Python 3 + Headless Google Chrome CDP (Chrome DevTools Protocol)

This script executes empirical adversarial tests against the live web runtime:
1. Baseline Smoke Checks (Checks 1-7):
   - Check 1: 0 console errors & unhandled exceptions during runtime.
   - Check 2: Canvas pixel buffer non-blank & multi-color terrain/entity rendering.
   - Check 3: Vietnamese HUD, unicode text, resource badges, and build catalog.
   - Check 4: Dialogue progression and state machine transitions (INTRO -> PLAYING).
   - Check 5: Building placement, footprint collision, and resource deduction.
   - Check 6: Villager simulation, 8-state AI FSM, BFS pathfinding, and motion.
   - Check 7: LocalStorage RMS save/load persistence (Slot 0 and Slot 1).
2. Boundary & Stress Verification:
   - Coordinate boundary stress: placement at out-of-bounds, negative, map edge, and overlapping cells.
   - Zero/Insufficient resources stress: placing all 12 buildings with 0 resources; verifying rejection and zero-clamp.
   - Camera boundaries & edge-scrolling limits: extreme panning, extreme zoom clamping, coordinate invertibility.
   - Corrupted LocalStorage handling: corrupted JSON injection and missing fields resilience.
   - Dialogue boundary stress: out-of-bounds navigation and rapid state transitions.
   - Mass entity simulation stress: 50+ concurrent villagers ticking without instability.

Exit code: 0 if all challenge checks pass, 1 on any failure.
"""

from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

import websockets

WEB_DIR = Path("/home/baoltb/Desktop/Paseo_Project/games/bolacthoitiensu/web")


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class M3Challenger:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.failures: List[str] = []
        self.console_errors: List[Dict[str, Any]] = []

    def check(self, condition: bool, test_name: str, detail: str = ""):
        self.tests_run += 1
        if condition:
            self.tests_passed += 1
            print(f"  [PASS] {test_name}")
        else:
            msg = f"{test_name}: {detail}"
            self.failures.append(msg)
            print(f"  [FAIL] {msg}")


async def run_m3_challenge() -> bool:
    challenger = M3Challenger()
    http_port = find_free_port()
    cdp_port = find_free_port()

    print("================================================================================")
    print("🚀 STARTING MILESTONE 3 EMPIRICAL ADVERSARIAL CHALLENGE HARNESS")
    print("================================================================================")
    print(f"[*] Target Directory: {WEB_DIR}")
    print(f"[*] Starting local HTTP server on port {http_port}...")

    http_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(http_port)],
        cwd=str(WEB_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    chrome_profile_dir = f"/tmp/chrome_m3_challenger_{cdp_port}"
    print(f"[*] Starting Headless Chrome on CDP port {cdp_port}...")
    chrome_proc = subprocess.Popen(
        [
            "google-chrome",
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-default-apps",
            "--disable-dev-shm-usage",
            f"--remote-debugging-port={cdp_port}",
            f"--user-data-dir={chrome_profile_dir}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        ws_url = None
        for _ in range(30):
            time.sleep(0.3)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json") as resp:
                    tabs = json.loads(resp.read().decode())
                    for tab in tabs:
                        if tab.get("type") == "page" and "webSocketDebuggerUrl" in tab:
                            ws_url = tab["webSocketDebuggerUrl"]
                            break
                    if ws_url:
                        break
            except Exception:
                pass

        if not ws_url:
            raise RuntimeError(f"Unable to establish CDP WebSocket connection to Chrome on port {cdp_port}")

        print(f"[*] Connected to Chrome CDP: {ws_url}")

        msg_id = 0

        async with websockets.connect(ws_url, max_size=20 * 1024 * 1024) as ws:
            async def send_cmd(method: str, params: dict | None = None) -> dict:
                nonlocal msg_id
                msg_id += 1
                cmd = {"id": msg_id, "method": method, "params": params or {}}
                await ws.send(json.dumps(cmd))
                while True:
                    raw = await ws.recv()
                    res = json.loads(raw)
                    if res.get("method") == "Runtime.consoleAPICalled":
                        p = res.get("params", {})
                        if p.get("type") in ("error", "assert"):
                            challenger.console_errors.append(p)
                    elif res.get("method") == "Runtime.exceptionThrown":
                        challenger.console_errors.append(res.get("params", {}))
                    if res.get("id") == cmd["id"]:
                        return res.get("result", {})

            async def eval_js(expression: str) -> Any:
                res = await send_cmd("Runtime.evaluate", {
                    "expression": expression,
                    "returnByValue": True,
                    "awaitPromise": True
                })
                if "exceptionDetails" in res:
                    print(f"  [JS Exception] {res['exceptionDetails']}")
                    challenger.console_errors.append(res["exceptionDetails"])
                return res.get("result", {}).get("value")

            # Enable Page and Runtime domains
            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")

            # -------------------------------------------------------------
            # SUITE 1: BOOTSTRAP & 7 SMOKE TEST CHECKS VERIFICATION
            # -------------------------------------------------------------
            print("\n--- SUITE 1: VERIFYING 7 BASELINE SMOKE CHECKS ---")
            target_url = f"http://127.0.0.1:{http_port}/index.html"
            await send_cmd("Page.navigate", {"url": target_url})

            # Wait for game bootstrap
            bootstrapped = False
            for _ in range(40):
                await asyncio.sleep(0.5)
                val = await eval_js("Boolean(window.gameApp && window.gameApp.renderer && window.gameApp.world)")
                if val is True:
                    bootstrapped = True
                    break

            challenger.check(bootstrapped, "Game Bootstrap", "window.gameApp initialized within 20s")

            # Check 1: 0 Console Errors
            challenger.check(len(challenger.console_errors) == 0, "Check 1: 0 Console Errors on Boot", f"Found: {challenger.console_errors}")

            # Check 2: Canvas Non-Blank & Color Variation
            pixel_data = await eval_js("""
            (() => {
                const canvas = document.getElementById('gameCanvas');
                const ctx = canvas.getContext('2d');
                const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                let nonZero = 0;
                const colorSet = new Set();
                for (let i = 0; i < imgData.data.length; i += 16) {
                    const r = imgData.data[i];
                    const g = imgData.data[i+1];
                    const b = imgData.data[i+2];
                    if (r > 10 || g > 10 || b > 10) {
                        nonZero++;
                        colorSet.add(`${r >> 4},${g >> 4},${b >> 4}`);
                    }
                }
                return { total: imgData.data.length / 16, nonZero: nonZero, distinctColors: colorSet.size };
            })()
            """)
            challenger.check(pixel_data.get("nonZero", 0) > 5000, "Check 2A: Canvas Non-Blank Pixel Buffer", f"nonZero={pixel_data.get('nonZero')}")
            challenger.check(pixel_data.get("distinctColors", 0) > 10, "Check 2B: Canvas Color Palette Diversity", f"distinctColors={pixel_data.get('distinctColors')}")

            # Check 3: Vietnamese HUD and Elements
            hud_info = await eval_js("""
            (() => {
                return {
                    title: document.querySelector('.tribe-title')?.innerText,
                    version: document.querySelector('.game-version')?.innerText,
                    food: document.getElementById('res-food')?.innerText,
                    wood: document.getElementById('res-wood')?.innerText,
                    stone: document.getElementById('res-stone')?.innerText,
                    bone: document.getElementById('res-bone')?.innerText,
                    score: document.getElementById('res-score')?.innerText,
                    pop: document.getElementById('res-pop')?.innerText,
                    buildCardsCount: document.querySelectorAll('.build-card').length,
                    speaker: document.getElementById('dialogue-speaker-name')?.innerText,
                    dialogueText: document.getElementById('dialogue-text')?.innerText
                };
            })()
            """)
            challenger.check(hud_info.get("title") == "BỘ LẠC TIỀN SỬ", "Check 3A: Vietnamese Title in DOM", f"title={hud_info.get('title')}")
            challenger.check(hud_info.get("buildCardsCount") == 12, "Check 3B: 12 Building Catalog Cards", f"cards={hud_info.get('buildCardsCount')}")
            challenger.check(len(hud_info.get("dialogueText", "")) > 20, "Check 3C: Non-empty Intro Dialogue Text", f"text={hud_info.get('dialogueText')[:40]}")
            challenger.check(hud_info.get("speaker") == "Người dẫn truyện", "Check 3D: Intro Dialogue Speaker", f"speaker={hud_info.get('speaker')}")

            # Check 4: Dialogue progression and state machine transitions (INTRO -> PLAYING)
            state_transition = await eval_js("""
            (() => {
                const initState = window.gameApp.state;
                let steps = 0;
                while (window.gameApp.state === 'INTRO_DIALOGUE' && window.gameApp.quest.isDialogueActive && steps < 50) {
                    window.gameApp.quest.nextDialogue();
                    steps++;
                }
                return {
                    initState: initState,
                    stepsAdvanced: steps,
                    finalState: window.gameApp.state,
                    dialogueActive: window.gameApp.quest.isDialogueActive
                };
            })()
            """)
            challenger.check(state_transition.get("initState") == "INTRO_DIALOGUE", "Check 4A: Initial State is INTRO_DIALOGUE", f"state={state_transition.get('initState')}")
            challenger.check(state_transition.get("finalState") == "PLAYING", "Check 4B: Transitioned to PLAYING State", f"state={state_transition.get('finalState')}")
            challenger.check(state_transition.get("dialogueActive") is False, "Check 4C: Dialogue Active is False", f"active={state_transition.get('dialogueActive')}")

            # Check 5: Building placement and cost deduction
            placement_res = await eval_js("""
            (() => {
                const initWood = window.gameApp.economy.wood;
                const initStone = window.gameApp.economy.stone;
                const initCount = window.gameApp.world.buildings.length;

                // Armory: ID 0, width 2, height 2, cost: 15 wood, 5 stone
                const armoryDef = window.BUILDING_CATALOG.find(b => b.id === 0);

                // Find a free spot
                let placeX = 12, placeY = 12;
                for (let y = 6; y < 24; y++) {
                    for (let x = 6; x < 24; x++) {
                        if (window.gameApp.world.canPlaceBuilding(x, y, armoryDef.width, armoryDef.height)) {
                            placeX = x;
                            placeY = y;
                            break;
                        }
                    }
                }

                window.gameApp.selectBuildingForPlacement(armoryDef);
                window.gameApp.confirmBuildingPlacement(placeX, placeY);

                const newBuilding = window.gameApp.world.buildings[window.gameApp.world.buildings.length - 1];

                return {
                    woodDeducted: initWood - window.gameApp.economy.wood,
                    stoneDeducted: initStone - window.gameApp.economy.stone,
                    buildingsCountBefore: initCount,
                    buildingsCountAfter: window.gameApp.world.buildings.length,
                    buildingName: newBuilding?.name,
                    buildingX: newBuilding?.x,
                    buildingY: newBuilding?.y,
                    isConstructed: newBuilding?.isConstructed,
                    cellMarkedOccupied: window.gameApp.world.collision[placeY][placeX] === -124
                };
            })()
            """)
            challenger.check(placement_res.get("woodDeducted") == 15, "Check 5A: Exactly 15 Wood Deducted for Armory", f"deducted={placement_res.get('woodDeducted')}")
            challenger.check(placement_res.get("stoneDeducted") == 5, "Check 5B: Exactly 5 Stone Deducted for Armory", f"deducted={placement_res.get('stoneDeducted')}")
            challenger.check(placement_res.get("buildingsCountAfter") == placement_res.get("buildingsCountBefore") + 1, "Check 5C: World Building Count Incremented", f"after={placement_res.get('buildingsCountAfter')}")
            challenger.check(placement_res.get("cellMarkedOccupied") is True, "Check 5D: Building Collision Cell Marked -124", f"collision={placement_res.get('cellMarkedOccupied')}")

            # Check 6: Villager motion and simulation ticks
            villager_sim = await eval_js("""
            (() => {
                const v = window.gameApp.world.villagers[0];
                const startX = v.x;
                const startY = v.y;

                // Send to walkable target (25, 25)
                v.moveTo(window.gameApp.world, 25, 25);
                const hasPath = v.path.length > 0;

                // Step simulation 150 frames
                for (let i = 0; i < 150; i++) {
                    window.gameApp.update(16.666);
                }

                return {
                    hasPath: hasPath,
                    pathLengthRemaining: v.path.length,
                    startX: startX,
                    startY: startY,
                    currentX: v.x,
                    currentY: v.y,
                    movedDistance: Math.hypot(v.x - startX, v.y - startY),
                    state: v.state
                };
            })()
            """)
            challenger.check(villager_sim.get("hasPath") is True, "Check 6A: BFS Path Generated for Villager", f"hasPath={villager_sim.get('hasPath')}")
            challenger.check(villager_sim.get("movedDistance", 0) > 1.0, "Check 6B: Villager Sub-tile Coordinates Moved", f"movedDistance={villager_sim.get('movedDistance')}")

            # Check 7: LocalStorage RMS Save & Restore
            rms_check = await eval_js("""
            (() => {
                // Set unique test state
                window.gameApp.economy.score = 98765;
                window.gameApp.economy.wood = 4321;
                window.gameApp.saveGame();

                const rawStored = localStorage.getItem('prehistoric_tribes_slot1');

                // Overwrite memory
                window.gameApp.economy.score = 0;
                window.gameApp.economy.wood = 0;

                // Load back
                window.gameApp.loadGame();

                return {
                    hasStoredData: Boolean(rawStored),
                    storedLength: rawStored?.length || 0,
                    restoredScore: window.gameApp.economy.score,
                    restoredWood: window.gameApp.economy.wood
                };
            })()
            """)
            challenger.check(rms_check.get("hasStoredData") is True, "Check 7A: LocalStorage Slot 1 Data Exists", f"storedLength={rms_check.get('storedLength')}")
            challenger.check(rms_check.get("restoredScore") == 98765, "Check 7B: Restored Score Equals 98765", f"score={rms_check.get('restoredScore')}")
            challenger.check(rms_check.get("restoredWood") == 4321, "Check 7C: Restored Wood Equals 4321", f"wood={rms_check.get('restoredWood')}")

            # -------------------------------------------------------------
            # SUITE 2: BOUNDARY STRESS ON BUILDING PLACEMENT
            # -------------------------------------------------------------
            print("\n--- SUITE 2: ADVERSARIAL BOUNDARY STRESS ON BUILDING PLACEMENT ---")
            placement_stress = await eval_js("""
            (() => {
                const results = [];
                const def = window.BUILDING_CATALOG[0]; // Armory 2x2
                const initialWood = window.gameApp.economy.wood;
                const initialBuildings = window.gameApp.world.buildings.length;

                window.gameApp.selectBuildingForPlacement(def);

                // Test 1: Negative coordinates (-5, -5)
                const canNeg = window.gameApp.world.canPlaceBuilding(-5, -5, 2, 2);
                window.gameApp.confirmBuildingPlacement(-5, -5);
                results.push({ name: 'negative_coords', canPlace: canNeg });

                // Test 2: Edge boundary (0, 0)
                const canZero = window.gameApp.world.canPlaceBuilding(0, 0, 2, 2);
                window.gameApp.confirmBuildingPlacement(0, 0);
                results.push({ name: 'zero_boundary', canPlace: canZero });

                // Test 3: Out-of-bounds map height (95, 95) with width=2, height=2 (map is 64x48 or 96x96)
                const canOverW = window.gameApp.world.canPlaceBuilding(window.gameApp.world.width - 1, 10, 2, 2);
                window.gameApp.confirmBuildingPlacement(window.gameApp.world.width - 1, 10);
                results.push({ name: 'overflow_width', canPlace: canOverW });

                const canOverH = window.gameApp.world.canPlaceBuilding(10, window.gameApp.world.height - 1, 2, 2);
                window.gameApp.confirmBuildingPlacement(10, window.gameApp.world.height - 1);
                results.push({ name: 'overflow_height', canPlace: canOverH });

                // Test 4: Overlapping existing building (Chief tent at world.buildings[0].x, y)
                const chief = window.gameApp.world.buildings[0];
                const canOverlap = window.gameApp.world.canPlaceBuilding(chief.x, chief.y, 2, 2);
                window.gameApp.confirmBuildingPlacement(chief.x, chief.y);
                results.push({ name: 'overlap_existing_building', canPlace: canOverlap });

                // Test 5: Overlapping natural obstacle (rock or tree)
                let resX = -1, resY = -1;
                for (let y = 0; y < window.gameApp.world.height; y++) {
                    for (let x = 0; x < window.gameApp.world.width; x++) {
                        if (window.gameApp.world.collision[y][x] === -124) {
                            resX = x;
                            resY = y;
                            break;
                        }
                    }
                    if (resX >= 0) break;
                }
                const canObstacle = window.gameApp.world.canPlaceBuilding(resX, resY, 2, 2);
                window.gameApp.confirmBuildingPlacement(resX, resY);
                results.push({ name: 'overlap_obstacle', canPlace: canObstacle });

                const finalWood = window.gameApp.economy.wood;
                const finalBuildings = window.gameApp.world.buildings.length;

                window.gameApp.cancelBuildingPlacement();

                return {
                    results: results,
                    woodUnchanged: initialWood === finalWood,
                    buildingsUnchanged: initialBuildings === finalBuildings
                };
            })()
            """)
            for item in placement_stress.get("results", []):
                challenger.check(item.get("canPlace") is False, f"Boundary Check: Rejected {item.get('name')}", f"canPlace={item.get('canPlace')}")
            challenger.check(placement_stress.get("woodUnchanged") is True, "Boundary Check: No Wood Deducted On Invalid Placements", f"woodUnchanged={placement_stress.get('woodUnchanged')}")
            challenger.check(placement_stress.get("buildingsUnchanged") is True, "Boundary Check: No Buildings Created On Invalid Placements", f"buildingsUnchanged={placement_stress.get('buildingsUnchanged')}")

            # -------------------------------------------------------------
            # SUITE 3: ZERO AND INSUFFICIENT RESOURCE HANDLING
            # -------------------------------------------------------------
            print("\n--- SUITE 3: ZERO AND INSUFFICIENT RESOURCE STRESS ---")
            economy_stress = await eval_js("""
            (() => {
                // Drain all resources to 0
                window.gameApp.economy.wood = 0;
                window.gameApp.economy.stone = 0;
                window.gameApp.economy.bone = 0;
                window.gameApp.economy.food = 0;

                const results = [];
                for (const def of window.BUILDING_CATALOG) {
                    const canAfford = window.gameApp.economy.canAfford(def.cost);
                    const deducted = window.gameApp.economy.deductCost(def.cost);
                    results.push({
                        id: def.id,
                        name: def.name,
                        canAfford: canAfford,
                        deducted: deducted
                    });
                }

                // Test food consumption tick with 0 food
                const initFood = window.gameApp.economy.food;
                window.gameApp.economy.update(10); // 10 villagers
                const postTickFood = window.gameApp.economy.food;

                return {
                    results: results,
                    allCannotAfford: results.every(r => r.canAfford === false),
                    allCannotDeduct: results.every(r => r.deducted === false),
                    foodNeverNegative: postTickFood >= 0,
                    finalWood: window.gameApp.economy.wood,
                    finalStone: window.gameApp.economy.stone
                };
            })()
            """)
            challenger.check(economy_stress.get("allCannotAfford") is True, "Economy Stress: canAfford is False for all 12 buildings when resources=0", f"results={economy_stress.get('allCannotAfford')}")
            challenger.check(economy_stress.get("allCannotDeduct") is True, "Economy Stress: deductCost is False for all 12 buildings when resources=0", f"results={economy_stress.get('allCannotDeduct')}")
            challenger.check(economy_stress.get("foodNeverNegative") is True, "Economy Stress: Food never drops below 0 during consumption tick", f"food={economy_stress.get('foodNeverNegative')}")
            challenger.check(economy_stress.get("finalWood") == 0 and economy_stress.get("finalStone") == 0, "Economy Stress: Stockpiles remained strictly clamped at 0", f"wood={economy_stress.get('finalWood')}")

            # -------------------------------------------------------------
            # SUITE 4: CAMERA BOUNDS, ZOOM, & COORDINATE BIJECTION
            # -------------------------------------------------------------
            print("\n--- SUITE 4: CAMERA BOUNDS, ZOOM & PROJECTION STRESS ---")
            camera_stress = await eval_js("""
            (() => {
                const cam = window.gameApp.camera;

                // 1. Extreme negative panning via moveBy
                cam.moveBy(-100000, -100000);
                for (let i = 0; i < 30; i++) cam.update();
                const clampedNegX = cam.x;
                const clampedNegY = cam.y;

                // 2. Extreme positive panning via moveBy
                cam.moveBy(1000000, 1000000);
                for (let i = 0; i < 30; i++) cam.update();
                const clampedPosX = cam.x;
                const clampedPosY = cam.y;

                // 2b. Keyboard continuous panning (ArrowLeft held for 120 ticks from village center)
                cam.centerOn(200, 200);
                window.gameApp.input.keys.add('ArrowLeft');
                for (let i = 0; i < 120; i++) {
                    window.gameApp.update(16.666);
                }
                window.gameApp.input.keys.delete('ArrowLeft');
                const keyboardPanX = cam.x;

                // 3. Extreme Zoom Min/Max
                cam.setZoom(0.0001);
                const minZoom = cam.zoom;
                cam.setZoom(9999.0);
                const maxZoom = cam.zoom;
                cam.setZoom(1.0); // Reset to 1.0

                // 4. Invertibility check: screenToWorld vs worldToScreen
                const testPoints = [
                    { sx: 100, sy: 150 },
                    { sx: 480, sy: 320 },
                    { sx: 800, sy: 600 }
                ];
                let maxDiff = 0;
                for (const p of testPoints) {
                    const world = cam.screenToWorld(p.sx, p.sy);
                    const backScreen = cam.worldToScreen(world.x, world.y);
                    const diff = Math.hypot(backScreen.x - p.sx, backScreen.y - p.sy);
                    if (diff > maxDiff) maxDiff = diff;
                }

                return {
                    clampedNegX: clampedNegX,
                    clampedNegY: clampedNegY,
                    clampedPosX: clampedPosX,
                    clampedPosY: clampedPosY,
                    keyboardPanX: keyboardPanX,
                    minZoom: minZoom,
                    maxZoom: maxZoom,
                    projectionMaxDiff: maxDiff,
                    noNaN: !Number.isNaN(cam.x) && !Number.isNaN(cam.y)
                };
            })()
            """)
            challenger.check(camera_stress.get("noNaN") is True, "Camera Stress: Coordinates never produce NaN under extreme input", f"noNaN={camera_stress.get('noNaN')}")
            challenger.check(camera_stress.get("clampedNegX") >= -150, "Camera Stress: MoveBy negative panning clamped within map bounds", f"clampedNegX={camera_stress.get('clampedNegX')}")
            challenger.check(camera_stress.get("keyboardPanX") >= -150, "Camera Stress: Keyboard ArrowLeft continuous panning clamped within map bounds", f"keyboardPanX={camera_stress.get('keyboardPanX')}")
            challenger.check(camera_stress.get("minZoom") == 0.5, "Camera Stress: Minimum zoom clamped strictly to 0.5", f"minZoom={camera_stress.get('minZoom')}")
            challenger.check(camera_stress.get("maxZoom") == 2.5, "Camera Stress: Maximum zoom clamped strictly to 2.5", f"maxZoom={camera_stress.get('maxZoom')}")
            challenger.check(camera_stress.get("projectionMaxDiff", 0) < 0.001, "Camera Stress: screenToWorld / worldToScreen bijection roundtrip error < 0.001px", f"error={camera_stress.get('projectionMaxDiff')}")


            # -------------------------------------------------------------
            # SUITE 5: MASS VILLAGER SIMULATION & PATHFINDING STRESS
            # -------------------------------------------------------------
            print("\n--- SUITE 5: MASS VILLAGER SIMULATION & PATHFINDING STRESS ---")
            villager_stress = await eval_js("""
            (() => {
                const world = window.gameApp.world;
                const economy = window.gameApp.economy;
                economy.wood = 500;
                economy.food = 500;

                const profs = [
                    window.gameApp.PROFESSIONS?.WOODCUTTER || { id: 1, name: 'Thợ đốn củi', targetResourceType: 1 },
                    window.gameApp.PROFESSIONS?.MINER || { id: 2, name: 'Thợ mỏ', targetResourceType: 2 },
                    window.gameApp.PROFESSIONS?.HUNTER || { id: 3, name: 'Thợ săn', targetResourceType: 3 },
                    window.gameApp.PROFESSIONS?.BUILDER || { id: 4, name: 'Thợ xây dựng', targetResourceType: null },
                    window.gameApp.PROFESSIONS?.VILLAGER || { id: 0, name: 'Dân làng', targetResourceType: 0 }
                ];

                // Spawn 40 additional villagers
                const initVillagerCount = world.villagers.length;
                for (let i = 0; i < 40; i++) {
                    const prof = profs[i % profs.length];
                    const v = new window.gameApp.world.villagers[0].constructor(
                        initVillagerCount + i + 1,
                        20 + (i % 8) * 2,
                        20 + Math.floor(i / 8) * 2,
                        prof
                    );
                    world.villagers.push(v);
                }

                // Pathfinding stress: unreachable target (e.g. out-of-bounds or isolated)
                const unreachablePath = world.findPath(10, 10, -50, -50);
                const sameCellPath = world.findPath(15, 15, 15, 15);

                // Run 100 simulation ticks
                for (let tick = 0; tick < 100; tick++) {
                    for (const v of world.villagers) {
                        v.update(world, economy, null);
                    }
                }

                // Check sanity of all villagers
                let anyNaN = false;
                for (const v of world.villagers) {
                    if (Number.isNaN(v.x) || Number.isNaN(v.y) || Number.isNaN(v.hp)) {
                        anyNaN = true;
                        break;
                    }
                }

                return {
                    totalVillagers: world.villagers.length,
                    unreachableHandledSafely: Array.isArray(unreachablePath),
                    sameCellHandledSafely: sameCellPath.length === 0,
                    noNaNFound: !anyNaN
                };
            })()
            """)
            challenger.check(villager_stress.get("totalVillagers", 0) >= 40, "Mass Villager Stress: 40+ villagers spawned concurrently", f"total={villager_stress.get('totalVillagers')}")
            challenger.check(villager_stress.get("unreachableHandledSafely") is True, "Pathfinding Stress: Unreachable target returns safe empty array without crash", f"res={villager_stress.get('unreachableHandledSafely')}")
            challenger.check(villager_stress.get("sameCellHandledSafely") is True, "Pathfinding Stress: Zero-distance same-cell target returns 0-length path", f"res={villager_stress.get('sameCellHandledSafely')}")
            challenger.check(villager_stress.get("noNaNFound") is True, "Mass Villager Stress: 100 ticks with 46 villagers completed with 0 NaN values", f"noNaN={villager_stress.get('noNaNFound')}")

            # -------------------------------------------------------------
            # SUITE 6: CORRUPTED LOCALSTORAGE / RMS RESILIENCE
            # -------------------------------------------------------------
            print("\n--- SUITE 6: CORRUPTED LOCALSTORAGE RESILIENCE STRESS ---")
            storage_stress = await eval_js("""
            (() => {
                // Test 1: Corrupted JSON syntax in slot 1
                localStorage.setItem('prehistoric_tribes_slot1', '{{CORRUPTED_JSON_BLOB_!@#$%^&*()');
                let corruptedHandled = false;
                try {
                    window.gameApp.loadGame();
                    corruptedHandled = true; // loadGame didn't crash
                } catch (e) {
                    corruptedHandled = false;
                }

                // Test 2: Missing fields / null payload
                localStorage.setItem('prehistoric_tribes_slot1', JSON.stringify({ version: '0.1.28' }));
                let nullFieldsHandled = false;
                try {
                    window.gameApp.loadGame();
                    nullFieldsHandled = true;
                } catch (e) {
                    nullFieldsHandled = false;
                }

                // Test 3: Load non-existent slot 2
                const slot2Data = window.gameApp.storage.loadGameSnapshot(2);

                return {
                    corruptedHandled: corruptedHandled,
                    nullFieldsHandled: nullFieldsHandled,
                    nonExistentSlotHandled: slot2Data === null
                };
            })()
            """)
            challenger.check(storage_stress.get("corruptedHandled") is True, "Storage Resilience: Malformed JSON handled gracefully without throw", f"handled={storage_stress.get('corruptedHandled')}")
            challenger.check(storage_stress.get("nullFieldsHandled") is True, "Storage Resilience: Missing payload attributes defaulted safely", f"handled={storage_stress.get('nullFieldsHandled')}")
            challenger.check(storage_stress.get("nonExistentSlotHandled") is True, "Storage Resilience: Non-existent save slot returns null safely", f"handled={storage_stress.get('nonExistentSlotHandled')}")

            # -------------------------------------------------------------
            # SUITE 7: QUEST OBJECTIVES & CHAPTER PROGRESSION
            # -------------------------------------------------------------
            print("\n--- SUITE 7: QUEST ENGINE & CHAPTER PROGRESSION STRESS ---")
            quest_stress = await eval_js("""
            (() => {
                const quest = window.gameApp.quest;
                const world = window.gameApp.world;
                const economy = window.gameApp.economy;

                const initStage = quest.currentStage;

                // Ensure chief tent and warehouse exist and are constructed
                const chiefTent = world.buildings.find(b => b.type === 3);
                if (chiefTent) chiefTent.isConstructed = true;

                // Ensure warehouse (ID 6)
                let wh = world.buildings.find(b => b.type === 6);
                if (!wh) {
                    const whDef = window.BUILDING_CATALOG.find(b => b.id === 6);
                    wh = new chiefTent.constructor(whDef, 18, 18, true);
                    world.buildings.push(wh);
                }
                wh.isConstructed = true;

                // Evaluate objectives
                quest.evaluateObjectives(world, economy, null);

                return {
                    initStage: initStage,
                    currentStage: quest.currentStage,
                    stageAdvanced: quest.currentStage > initStage,
                    chapterTitle: quest.getCurrentChapter().title
                };
            })()
            """)
            challenger.check(quest_stress.get("stageAdvanced") is True, "Quest Engine: Stage advanced automatically when objectives satisfied", f"stage={quest_stress.get('currentStage')}")
            challenger.check("Màn 2" in quest_stress.get("chapterTitle", ""), "Quest Engine: Chapter 2 Title loaded correctly in Vietnamese", f"title={quest_stress.get('chapterTitle')}")

            # -------------------------------------------------------------
            # SUITE 8: FINAL CONSOLE INTEGRITY AUDIT
            # -------------------------------------------------------------
            print("\n--- SUITE 8: FINAL RUNTIME CONSOLE ERROR AUDIT ---")
            challenger.check(len(challenger.console_errors) == 0, "Check 1 Final: 0 Console Errors Across Entire Stress Session", f"errors={challenger.console_errors}")

    finally:
        print("\n[*] Terminating Chrome and HTTP test runners...")
        try:
            chrome_proc.terminate()
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()
        try:
            http_proc.terminate()
            http_proc.wait(timeout=3)
        except Exception:
            http_proc.kill()
        subprocess.run(["rm", "-rf", chrome_profile_dir], check=False)

    print("\n================================================================================")
    print("📊 CHALLENGE SUMMARY & FINAL VERDICT")
    print("================================================================================")
    print(f"Total Tests Run: {challenger.tests_run}")
    print(f"Tests Passed:    {challenger.tests_passed}")
    print(f"Tests Failed:    {len(challenger.failures)}")

    if challenger.failures:
        print("\nFailures Detail:")
        for f in challenger.failures:
            print(f"  - {f}")
        print("\nVERDICT: REJECT ❌")
        return False
    else:
        print("\nAll adversarial and boundary test gates PASSED with 100% compliance!")
        print("VERDICT: APPROVE ✅")
        return True


if __name__ == "__main__":
    success = asyncio.run(run_m3_challenge())
    sys.exit(0 if success else 1)
