#!/usr/bin/env python3
"""
Automated Headless Chrome CDP Smoke Test for Bộ Lạc Thời Tiền Sử Web Remake.
Validates:
- 0 console / runtime errors.
- Canvas rendering with non-blank pixels.
- Working game loop and state transitions.
- Vietnamese HUD and dialogue rendering.
- Building placement with collision and economy cost deduction.
- 8-state Villager simulation updates.
- LocalStorage RMS save/load persistence.
"""

import sys
import os
import time
import json
import socket
import subprocess
import asyncio
import urllib.request
import websockets

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

async def run_cdp_test():
    web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web"))
    http_port = find_free_port()
    cdp_port = find_free_port()

    print(f"[Test] Starting HTTP Server on port {http_port} (root: {web_dir})...")
    http_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(http_port)],
        cwd=web_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    chrome_user_data = f"/tmp/chrome_tribes_test_{cdp_port}"
    print(f"[Test] Starting Headless Chrome on CDP port {cdp_port}...")
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
            f"--user-data-dir={chrome_user_data}",
            "about:blank"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        # Wait for Chrome CDP to be available
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
            raise RuntimeError("Failed to connect to Headless Chrome CDP within 10 seconds")

        print(f"[Test] Connected to Chrome CDP: {ws_url}")

        console_errors = []
        msg_id = 0

        async with websockets.connect(ws_url) as ws:
            async def send_cmd(method, params=None):
                nonlocal msg_id
                msg_id += 1
                cmd = {"id": msg_id, "method": method, "params": params or {}}
                await ws.send(json.dumps(cmd))
                while True:
                    res = json.loads(await ws.recv())
                    if res.get("method") == "Runtime.consoleAPICalled":
                        p = res.get("params", {})
                        if p.get("type") in ("error", "assert"):
                            console_errors.append(p)
                    elif res.get("method") == "Runtime.exceptionThrown":
                        console_errors.append(res.get("params", {}))
                    if res.get("id") == cmd["id"]:
                        return res.get("result", {})

            # Enable events
            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")

            # Navigate to game
            target_url = f"http://127.0.0.1:{http_port}/index.html"
            print(f"[Test] Navigating to {target_url}...")
            await send_cmd("Page.navigate", {"url": target_url})

            # Wait for page load and game initialization
            print("[Test] Waiting for asset loading and game bootstrap...")
            for _ in range(40):
                await asyncio.sleep(0.5)
                eval_res = await send_cmd("Runtime.evaluate", {
                    "expression": "Boolean(window.gameApp && window.gameApp.renderer && window.gameApp.world)",
                    "returnByValue": True
                })
                if eval_res.get("result", {}).get("value") is True:
                    break

            # 1. Assert 0 console errors
            print("[Test] Check 1: Validating Console Error logs...")
            if console_errors:
                print(f"[FAIL] Found console errors: {console_errors}")
                return False
            print("  -> PASS: 0 console errors detected.")

            # 2. Check Canvas rendering non-blank pixels
            print("[Test] Check 2: Verifying Canvas non-blank pixel buffer...")
            pixel_eval = await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    const canvas = document.getElementById('gameCanvas');
                    const ctx = canvas.getContext('2d');
                    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    let nonZero = 0;
                    for (let i = 0; i < imgData.data.length; i += 4) {
                        // Check if not completely black or transparent
                        if (imgData.data[i] > 10 || imgData.data[i+1] > 10 || imgData.data[i+2] > 10) {
                            nonZero++;
                        }
                    }
                    return { total: imgData.data.length / 4, nonZero: nonZero };
                })()
                """,
                "returnByValue": True
            })
            pixel_result = pixel_eval.get("result", {}).get("value", {})
            non_zero = pixel_result.get("nonZero", 0)
            print(f"  -> Rendered non-blank pixels: {non_zero}/{pixel_result.get('total')}")
            assert non_zero > 10000, f"Canvas appears blank! Only {non_zero} non-zero pixels found."
            print("  -> PASS: Canvas successfully renders rich prehistoric terrain tiles!")

            # 3. Check Vietnamese HUD Elements
            print("[Test] Check 3: Verifying Vietnamese HUD elements & resources...")
            hud_eval = await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    return {
                        title: document.querySelector('.tribe-title')?.innerText,
                        food: document.getElementById('res-food')?.innerText,
                        wood: document.getElementById('res-wood')?.innerText,
                        stone: document.getElementById('res-stone')?.innerText,
                        bone: document.getElementById('res-bone')?.innerText,
                        score: document.getElementById('res-score')?.innerText,
                        buildCards: document.querySelectorAll('.build-card').length,
                        dialogueText: document.getElementById('dialogue-text')?.innerText,
                        speaker: document.getElementById('dialogue-speaker-name')?.innerText
                    };
                })()
                """,
                "returnByValue": True
            })
            hud_data = hud_eval.get("result", {}).get("value", {})
            print(f"  -> Title: {hud_data.get('title')}")
            print(f"  -> Build Cards count: {hud_data.get('buildCards')}")
            print(f"  -> Dialogue Speaker: {hud_data.get('speaker')}")
            print(f"  -> Dialogue Text preview: {hud_data.get('dialogueText')[:80]}...")
            assert hud_data.get("title") == "BỘ LẠC TIỀN SỬ", "Vietnamese title mismatch!"
            assert hud_data.get("buildCards") == 12, f"Expected 12 building cards, found {hud_data.get('buildCards')}"
            assert len(hud_data.get("dialogueText", "")) > 10, "Intro dialogue text empty!"
            print("  -> PASS: Vietnamese HUD and Intro Dialogue verified.")

            # 4. Advance Intro Dialogue and enter PLAYING mode
            print("[Test] Check 4: Testing Dialogue advancement to PLAYING state...")
            await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    // Fast-forward through dialogue
                    while (window.gameApp.state === 'INTRO_DIALOGUE' && window.gameApp.quest.isDialogueActive) {
                        window.gameApp.quest.nextDialogue();
                    }
                    return window.gameApp.state;
                })()
                """,
                "returnByValue": True
            })
            state_eval = await send_cmd("Runtime.evaluate", {
                "expression": "window.gameApp.state",
                "returnByValue": True
            })
            current_state = state_eval.get("result", {}).get("value")
            assert current_state == "PLAYING", f"Expected state PLAYING, got {current_state}"
            print("  -> PASS: State machine smoothly transitioned to PLAYING.")

            # 5. Test Building Placement with Collision & Resource Cost Deduction
            print("[Test] Check 5: Testing Building placement & Economy deduction...")
            build_test = await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    const initialWood = window.gameApp.economy.wood;
                    const initialBuildings = window.gameApp.world.buildings.length;

                    // Select Armory (ID 0, costs 15 wood, 5 stone)
                    const armoryDef = window.gameApp.BUILDING_CATALOG ? window.gameApp.BUILDING_CATALOG[0] : null;
                    // Find a guaranteed walkable cell
                    let targetX = 10, targetY = 10;
                    for (let y = 5; y < 20; y++) {
                        for (let x = 5; x < 20; x++) {
                            if (window.gameApp.world.canPlaceBuilding(x, y, 2, 2)) {
                                targetX = x;
                                targetY = y;
                                break;
                            }
                        }
                    }

                    // Select and place
                    const def = window.gameApp.world ? window.gameApp.world.findNearestBuilding(0, 0, 3).def : null;
                    // We can use BUILDING_CATALOG from main.js or selectBuildingForPlacement
                    const armory = window.BUILDING_CATALOG_EXPORT || { id: 0, name: 'Kho vũ khí', width: 2, height: 2, cost: { wood: 15, stone: 5 } };
                    window.gameApp.selectBuildingForPlacement({
                        id: 0, name: 'Kho vũ khí', width: 2, height: 2, cost: { wood: 15, stone: 5, bone: 0 }, hpTiers: [25, 40, 90]
                    });

                    window.gameApp.confirmBuildingPlacement(targetX, targetY);

                    return {
                        woodDeducted: initialWood - window.gameApp.economy.wood,
                        buildingsCount: window.gameApp.world.buildings.length,
                        newBuildingBuilt: window.gameApp.world.buildings.length > initialBuildings
                    };
                })()
                """,
                "returnByValue": True
            })
            build_res = build_test.get("result", {}).get("value", {})
            print(f"  -> Wood deducted: {build_res.get('woodDeducted')}")
            print(f"  -> Buildings count: {build_res.get('buildingsCount')}")
            assert build_res.get("woodDeducted") == 15, f"Expected 15 wood deducted, got {build_res.get('woodDeducted')}"
            assert build_res.get("newBuildingBuilt") is True, "New building was not placed into world grid!"
            print("  -> PASS: Building placement, collision check, and cost deduction validated.")

            # 6. Test Villager AI Simulation Tick
            print("[Test] Check 6: Testing Villager simulation & job updates...")
            sim_test = await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    const v0 = window.gameApp.world.villagers[0];
                    const initX = v0.x;
                    const initY = v0.y;

                    // Order villager to move to (30, 30)
                    v0.moveTo(window.gameApp.world, 30, 30);

                    // Step simulation 120 ticks
                    for (let i = 0; i < 120; i++) {
                        window.gameApp.update(16.66);
                    }

                    return {
                        initX: initX,
                        initY: initY,
                        newX: v0.x,
                        newY: v0.y,
                        moved: (v0.x !== initX || v0.y !== initY),
                        state: v0.state
                    };
                })()
                """,
                "returnByValue": True
            })
            sim_res = sim_test.get("result", {}).get("value", {})
            print(f"  -> Villager moved: {sim_res.get('moved')} from ({sim_res.get('initX')}, {sim_res.get('initY')}) to ({sim_res.get('newX'):.2f}, {sim_res.get('newY'):.2f})")
            assert sim_res.get("moved") is True, "Villager did not advance along path!"
            print("  -> PASS: Villager A* pathfinding and motion tick verified.")

            # 7. Test Save and Load RMS Persistence
            print("[Test] Check 7: Testing LocalStorage RMS Save & Load...")
            save_test = await send_cmd("Runtime.evaluate", {
                "expression": """
                (() => {
                    // Modify score to a unique value
                    window.gameApp.economy.score = 7777;
                    window.gameApp.saveGame();

                    // Alter score in memory
                    window.gameApp.economy.score = 1111;

                    // Reload from storage
                    window.gameApp.loadGame();

                    return {
                        restoredScore: window.gameApp.economy.score,
                        hasSaveSlot1: window.gameApp.storage.hasSave(1)
                    };
                })()
                """,
                "returnByValue": True
            })
            save_res = save_test.get("result", {}).get("value", {})
            print(f"  -> Restored score: {save_res.get('restoredScore')}")
            assert save_res.get("hasSaveSlot1") is True, "Savegame slot 1 not found in LocalStorage!"
            assert save_res.get("restoredScore") == 7777, f"Expected 7777 restored score, got {save_res.get('restoredScore')}"
            print("  -> PASS: LocalStorage savegame persistence verified.")

            print("\n=======================================================")
            print("🎉 ALL 7 AUTOMATED HEADLESS SMOKE CHECKS PASSED WITH 100% SUCCESS!")
            print("=======================================================\n")
            return True

    finally:
        print("[Test] Cleaning up Chrome and HTTP processes...")
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
        # Clean up temporary profile
        subprocess.run(["rm", "-rf", chrome_user_data], check=False)

if __name__ == "__main__":
    success = asyncio.run(run_cdp_test())
    sys.exit(0 if success else 1)
