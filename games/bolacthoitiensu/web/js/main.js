/**
 * Main Application Bootstrap (web/js/main.js)
 * Coordinates engine subsystems, fixed delta game loop, state machine, and HUD wiring.
 */

import { AssetLoader } from './engine/loader.js';
import { CanvasRenderer } from './engine/renderer.js';
import { Camera } from './engine/camera.js';
import { InputManager } from './engine/input.js';
import { GameStorage } from './engine/storage.js';
import { AudioManager } from './engine/audio.js';

import { WorldGrid } from './game/world.js';
import { BUILDING_CATALOG, BuildingInstance } from './game/building.js';
import { Villager, PROFESSIONS } from './game/villager.js';
import { Economy } from './game/economy.js';
import { QuestEngine } from './game/quest.js';

export const GAME_STATES = {
    INTRO_DIALOGUE: 'INTRO_DIALOGUE',
    PLAYING: 'PLAYING',
    BUILDING_PLACEMENT: 'BUILDING_PLACEMENT',
    QUEST_DIALOGUE: 'QUEST_DIALOGUE',
    PAUSED: 'PAUSED'
};

class PrehistoricTribesApp {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.loader = new AssetLoader();
        this.storage = new GameStorage();
        this.audio = new AudioManager();

        this.renderer = null;
        this.camera = null;
        this.input = null;

        this.world = null;
        this.economy = new Economy();
        this.quest = null;

        this.state = GAME_STATES.INTRO_DIALOGUE;
        this.selectedEntity = null;
        this.placingBuildingDef = null;

        // Timing loop
        this.lastTime = performance.now();
        this.accumulator = 0;
        this.FIXED_DELTA = 1000 / 60; // 16.666 ms
    }

    async init() {
        console.log('[App] Initializing Bộ Lạc Thời Tiền Sử Web Remake...');

        // 1. Preload all assets
        await this.loader.preloadAll((loaded, total) => {
            // Optional progress log
        });

        // 2. Initialize renderer and camera
        this.renderer = new CanvasRenderer(this.canvas, this.loader);
        this.camera = new Camera(this.canvas.width, this.canvas.height);
        this.input = new InputManager(this.canvas, this.camera);

        // 3. Initialize world and quest
        const mapsData = this.loader.getJSON('maps');
        const locData = this.loader.getJSON('localization');

        this.world = new WorldGrid(mapsData);
        this.quest = new QuestEngine(locData);

        // Set camera bounds
        this.camera.setMapBounds(this.world.width, this.world.height, 22, 16);

        // 4. Populate starting prehistoric village
        this.setupInitialVillage();

        // 5. Wire UI events and HUD
        this.setupUI();
        this.bindEvents();

        // 6. Handle responsive resize
        this.handleResize();
        window.addEventListener('resize', () => this.handleResize());

        // 7. Load sound settings from slot 0
        const slot0 = this.storage.loadSlot0();
        this.audio.enabled = slot0.soundEnabled ?? true;
        this.updateSoundBtn();

        // 8. Start Intro Dialogue sequence
        this.state = GAME_STATES.INTRO_DIALOGUE;
        this.quest.startIntroDialogue();

        // 9. Start 60 FPS requestAnimationFrame loop
        requestAnimationFrame((t) => this.gameLoop(t));
        console.log('[App] Game loop started successfully.');
    }

    /**
     * Creates starting village buildings and villagers around map center
     */
    setupInitialVillage() {
        const cx = Math.floor(this.world.width / 2);
        const cy = Math.floor(this.world.height / 2);

        // Chief's Tent (Lều của Tù trưởng, ID 3, 4x4)
        const chiefDef = BUILDING_CATALOG.find(b => b.id === 3);
        const chiefTent = new BuildingInstance(chiefDef, cx - 2, cy - 2, true);
        this.world.buildings.push(chiefTent);
        this.world.occupyFootprint(chiefTent.x, chiefTent.y, chiefTent.width, chiefTent.height);

        // Starting Hut (Lều, ID 2, 5x4)
        const tentDef = BUILDING_CATALOG.find(b => b.id === 2);
        const hut = new BuildingInstance(tentDef, cx + 5, cy - 2, true);
        this.world.buildings.push(hut);
        this.world.occupyFootprint(hut.x, hut.y, hut.width, hut.height);

        // Spawn 6 starting villagers
        const startingJobs = [
            PROFESSIONS.WOODCUTTER,
            PROFESSIONS.VILLAGER,
            PROFESSIONS.MINER,
            PROFESSIONS.BUILDER,
            PROFESSIONS.HUNTER,
            PROFESSIONS.VILLAGER
        ];

        for (let i = 0; i < 6; i++) {
            const vx = cx + (i % 3) * 2 - 2;
            const vy = cy + Math.floor(i / 3) * 2 + 4;
            const villager = new Villager(i + 1, vx, vy, startingJobs[i]);
            this.world.villagers.push(villager);
        }

        // Focus camera on Chief Tent
        this.camera.centerOn(cx * 22, cy * 16);
    }

    /**
     * Wires DOM HUD elements, buttons, and panels
     */
    setupUI() {
        // Render Build Catalog Cards
        const catalogContainer = document.getElementById('build-catalog');
        catalogContainer.innerHTML = '';

        BUILDING_CATALOG.forEach(b => {
            const card = document.createElement('div');
            card.className = 'build-card';
            card.dataset.buildingId = b.id;

            const costText = [];
            if (b.cost.wood) costText.push(`🪵 ${b.cost.wood}`);
            if (b.cost.stone) costText.push(`🪨 ${b.cost.stone}`);
            if (b.cost.bone) costText.push(`🦴 ${b.cost.bone}`);

            card.innerHTML = `
                <div class="build-card-header">
                    <span class="build-card-icon">${b.icon}</span>
                    <span class="build-card-name" title="${b.name} (${b.width}x${b.height})">${b.name}</span>
                </div>
                <div class="build-card-costs">
                    ${costText.map(c => `<span class="cost-tag">${c}</span>`).join('')}
                </div>
            `;

            card.addEventListener('click', () => {
                this.selectBuildingForPlacement(b);
            });

            catalogContainer.appendChild(card);
        });

        // Economy HUD listener
        this.economy.onResourceChanged = (res) => {
            document.getElementById('res-food').innerText = Math.floor(res.food);
            document.getElementById('res-wood').innerText = Math.floor(res.wood);
            document.getElementById('res-stone').innerText = Math.floor(res.stone);
            document.getElementById('res-bone').innerText = Math.floor(res.bone);
            document.getElementById('res-score').innerText = Math.floor(res.score);

            const popCap = this.economy.getPopulationCap(this.world.buildings);
            document.getElementById('res-pop').innerText = `${this.world.villagers.length}/${popCap}`;

            this.updateBuildMenuAffordability();
        };

        this.economy.notifyChange();

        // Quest dialogue modal callbacks
        this.quest.onDialogueShow = (data) => {
            const modal = document.getElementById('dialogue-modal');
            const portrait = document.getElementById('dialogue-portrait');
            const speaker = document.getElementById('dialogue-speaker-name');
            const msg = document.getElementById('dialogue-text');
            const btnPrev = document.getElementById('btn-dialogue-prev');
            const btnNext = document.getElementById('btn-dialogue-next');

            modal.classList.remove('hidden');
            portrait.src = data.portrait;
            speaker.innerText = data.speaker;
            msg.innerText = data.text;

            btnPrev.style.display = data.hasPrev ? 'inline-block' : 'none';
            btnNext.innerText = data.hasNext ? 'Tiếp tục ▸' : 'Bắt đầu chơi ✓';
        };

        this.quest.onDialogueHide = () => {
            document.getElementById('dialogue-modal').classList.add('hidden');
            if (this.state === GAME_STATES.INTRO_DIALOGUE || this.state === GAME_STATES.QUEST_DIALOGUE) {
                this.state = GAME_STATES.PLAYING;
            }
        };

        this.quest.onQuestCompleted = (chapter) => {
            this.showToast(`🎉 Hoàn thành nhiệm vụ! Chuyển sang ${chapter.title}`, 'success');
        };
    }

    /**
     * Binds click and key input handlers
     */
    bindEvents() {
        // Tile Click: Select entity or place building
        this.input.onTileClick = (gx, gy, wx, wy) => {
            this.audio.playClick();

            if (this.state === GAME_STATES.BUILDING_PLACEMENT && this.placingBuildingDef) {
                this.confirmBuildingPlacement(gx, gy);
                return;
            }

            // Normal entity selection
            const entity = this.world.getEntityAt(gx, gy);
            this.selectedEntity = entity;
            this.updateInspector(entity);
        };

        // Cancel action (Right click or ESC)
        this.input.onCancel = () => {
            if (this.state === GAME_STATES.BUILDING_PLACEMENT) {
                this.cancelBuildingPlacement();
            } else if (this.selectedEntity) {
                this.selectedEntity = null;
                this.updateInspector(null);
            }
        };

        // Dialogue modal buttons
        document.getElementById('btn-dialogue-next').addEventListener('click', () => {
            this.audio.playClick();
            this.quest.nextDialogue();
        });

        document.getElementById('btn-dialogue-prev').addEventListener('click', () => {
            this.audio.playClick();
            this.quest.prevDialogue();
        });

        document.getElementById('btn-dialogue-close').addEventListener('click', () => {
            this.audio.playClick();
            this.quest.closeDialogue();
        });

        // Cancel placement button
        document.getElementById('btn-cancel-placement').addEventListener('click', () => {
            this.cancelBuildingPlacement();
        });

        // Top bar buttons
        document.getElementById('btn-save').addEventListener('click', () => {
            this.saveGame();
        });

        document.getElementById('btn-load').addEventListener('click', () => {
            this.loadGame();
        });

        document.getElementById('btn-sound').addEventListener('click', () => {
            const enabled = this.audio.toggleSound();
            this.updateSoundBtn();
            this.storage.saveSlot0({ soundEnabled: enabled });
            this.showToast(enabled ? '🔊 Đã bật âm thanh' : '🔇 Đã tắt âm thanh');
        });

        document.getElementById('btn-quest-log').addEventListener('click', () => {
            this.openQuestLog();
        });

        document.getElementById('btn-quest-log-close').addEventListener('click', () => {
            document.getElementById('quest-log-modal').classList.add('hidden');
        });

        document.getElementById('btn-close-quest-log').addEventListener('click', () => {
            document.getElementById('quest-log-modal').classList.add('hidden');
        });
    }

    updateSoundBtn() {
        const btn = document.getElementById('btn-sound');
        btn.innerText = this.audio.enabled ? '🔊 Âm thanh' : '🔇 Âm thanh';
    }

    /**
     * Begins building placement mode
     */
    selectBuildingForPlacement(buildingDef) {
        if (!this.economy.canAfford(buildingDef.cost)) {
            this.audio.playError();
            this.showToast(`Không đủ tài nguyên để xây ${buildingDef.name}!`, 'error');
            return;
        }

        // Check prerequisite
        if (buildingDef.prerequisiteId !== null && buildingDef.prerequisiteId !== undefined) {
            const prereqBuilt = this.world.buildings.some(b => b.type === buildingDef.prerequisiteId && b.isConstructed);
            if (!prereqBuilt) {
                const reqName = BUILDING_CATALOG.find(b => b.id === buildingDef.prerequisiteId)?.name || 'công trình yêu cầu';
                this.audio.playError();
                this.showToast(`Cần xây dựng ${reqName} trước!`, 'error');
                return;
            }
        }

        this.placingBuildingDef = buildingDef;
        this.state = GAME_STATES.BUILDING_PLACEMENT;

        document.getElementById('placement-overlay').classList.remove('hidden');
        document.getElementById('placement-building-name').innerText = buildingDef.name;

        // Highlight selected build card
        document.querySelectorAll('.build-card').forEach(c => {
            c.classList.toggle('selected', Number(c.dataset.buildingId) === buildingDef.id);
        });

        this.audio.playClick();
    }

    confirmBuildingPlacement(gx, gy) {
        if (!this.placingBuildingDef) return;

        const def = this.placingBuildingDef;
        const canPlace = this.world.canPlaceBuilding(gx, gy, def.width, def.height);

        if (!canPlace) {
            this.audio.playError();
            this.showToast('Vị trí này bị vướng vật cản hoặc ngoài bản đồ!', 'error');
            return;
        }

        // Deduct cost
        if (!this.economy.deductCost(def.cost)) {
            this.audio.playError();
            this.showToast('Không đủ tài nguyên!', 'error');
            return;
        }

        // Create new building instance under construction
        const newBuilding = new BuildingInstance(def, gx, gy, false);
        this.world.buildings.push(newBuilding);
        this.world.occupyFootprint(gx, gy, def.width, def.height);

        this.audio.playBuild();
        this.showToast(`Đã bắt đầu dựng ${def.name}. Dân làng sẽ đến thi công!`, 'success');

        // Automatically dispatch idle or builder villagers to help construct
        const builders = this.world.villagers.filter(v => v.profession.id === PROFESSIONS.BUILDER.id || v.state === 0);
        builders.forEach(b => {
            b.targetEntity = newBuilding;
            b.moveTo(this.world, newBuilding.x + 1, newBuilding.y + 1);
        });

        this.cancelBuildingPlacement();
    }

    cancelBuildingPlacement() {
        this.placingBuildingDef = null;
        this.state = GAME_STATES.PLAYING;
        document.getElementById('placement-overlay').classList.add('hidden');
        document.querySelectorAll('.build-card').forEach(c => c.classList.remove('selected'));
    }

    /**
     * Updates build card affordability visuals
     */
    updateBuildMenuAffordability() {
        document.querySelectorAll('.build-card').forEach(card => {
            const bId = Number(card.dataset.buildingId);
            const def = BUILDING_CATALOG.find(b => b.id === bId);
            if (def) {
                const canAfford = this.economy.canAfford(def.cost);
                card.classList.toggle('disabled', !canAfford);
            }
        });
    }

    /**
     * Populates entity inspector panel when a villager or building is clicked
     */
    updateInspector(entity) {
        const inspectorBody = document.getElementById('inspector-content');
        const inspectorSub = document.getElementById('inspector-target-type');

        if (!entity) {
            inspectorSub.innerText = 'Chưa chọn đơn vị nào';
            inspectorBody.innerHTML = '<div class="empty-state">Nhấn vào dân làng hoặc công trình trên bản đồ để xem chi tiết và giao nhiệm vụ.</div>';
            return;
        }

        if (entity instanceof Villager) {
            inspectorSub.innerText = `Dân làng #${entity.id}`;
            inspectorBody.innerHTML = `
                <div class="entity-info-card">
                    <div class="info-row-top">
                        <span class="entity-name">${entity.name}</span>
                        <span class="badge">${entity.profession.name}</span>
                    </div>
                    <div class="entity-hp-bar">
                        <div class="entity-hp-fill" style="width: ${(entity.hp / entity.maxHp) * 100}%"></div>
                    </div>
                    <div class="info-details">
                        <span>Máu: ${Math.floor(entity.hp)}/${entity.maxHp}</span>
                        <span>Thể lực: ${Math.floor(entity.stamina)}/${entity.maxStamina}</span>
                        <span>Vị trí: (${Math.floor(entity.x)}, ${Math.floor(entity.y)})</span>
                        <span>Đang mang: ${entity.carriedAmount > 0 ? `${entity.carriedAmount} tài nguyên` : 'Trống'}</span>
                    </div>
                    <div class="section-title" style="margin-top: 6px;">Phân công công việc:</div>
                    <div class="job-actions">
                        <button class="job-btn ${entity.profession.id === 0 ? 'active' : ''}" data-job="0">🧺 Hái lượm</button>
                        <button class="job-btn ${entity.profession.id === 1 ? 'active' : ''}" data-job="1">🪓 Đốn củi</button>
                        <button class="job-btn ${entity.profession.id === 2 ? 'active' : ''}" data-job="2">⛏️ Khai thác</button>
                        <button class="job-btn ${entity.profession.id === 3 ? 'active' : ''}" data-job="3">🏹 Săn bắn</button>
                        <button class="job-btn ${entity.profession.id === 4 ? 'active' : ''}" data-job="4">🔨 Xây dựng</button>
                    </div>
                </div>
            `;

            inspectorBody.querySelectorAll('.job-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const jobId = Number(btn.dataset.job);
                    const profKey = Object.keys(PROFESSIONS).find(k => PROFESSIONS[k].id === jobId);
                    if (profKey) {
                        entity.assignJob(PROFESSIONS[profKey]);
                        this.audio.playClick();
                        this.updateInspector(entity);
                        this.showToast(`Đã phân công ${entity.name} làm ${PROFESSIONS[profKey].name}`);
                    }
                });
            });

        } else if (entity instanceof BuildingInstance) {
            inspectorSub.innerText = `Công trình: ${entity.name}`;
            inspectorBody.innerHTML = `
                <div class="entity-info-card">
                    <div class="info-row-top">
                        <span class="entity-name">${entity.name}</span>
                        <span class="badge">Cấp ${entity.level}</span>
                    </div>
                    <div class="entity-hp-bar">
                        <div class="entity-hp-fill" style="width: ${(entity.hp / entity.maxHp) * 100}%"></div>
                    </div>
                    <div class="info-details">
                        <span>Độ bền: ${entity.hp}/${entity.maxHp} HP</span>
                        <span>Kích thước: ${entity.width}x${entity.height} ô</span>
                        <span>Trạng thái: ${entity.isConstructed ? 'Hoạt động tốt' : `Đang xây dựng (${entity.constructionProgress}%)`}</span>
                        <span>Tọa độ: (${entity.x}, ${entity.y})</span>
                    </div>
                    <p style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">${entity.def.desc}</p>
                </div>
            `;
        }
    }

    /**
     * Opens quest log modal with current objectives checklist
     */
    openQuestLog() {
        const chapter = this.quest.getCurrentChapter();
        document.getElementById('quest-chapter-title').innerText = chapter.title;
        document.getElementById('quest-objective-desc').innerText = chapter.description;

        const tasksList = document.getElementById('quest-tasks-list');
        tasksList.innerHTML = '';

        chapter.objectives.forEach(obj => {
            const isDone = this.quest.completedObjectives.has(obj.id);
            const li = document.createElement('li');
            li.className = `quest-item ${isDone ? 'completed' : ''}`;
            li.innerHTML = `
                <span class="quest-check">${isDone ? '✅' : '⬜'}</span>
                <span>${obj.text}</span>
            `;
            tasksList.appendChild(li);
        });

        document.getElementById('quest-log-modal').classList.remove('hidden');
        this.audio.playClick();
    }

    /**
     * Saves snapshot to Slot 1
     */
    saveGame() {
        const gameState = {
            levelIndex: this.world.levelIndex,
            questStage: this.quest.currentStage,
            resources: {
                food: this.economy.food,
                wood: this.economy.wood,
                stone: this.economy.stone,
                bone: this.economy.bone,
                score: this.economy.score
            },
            villagers: this.world.villagers,
            buildings: this.world.buildings
        };

        const success = this.storage.saveGameSnapshot(1, gameState);
        if (success) {
            this.audio.playFanfare();
            this.showToast('💾 Đã lưu tiến trình thành công vào Khe 1!', 'success');
        } else {
            this.audio.playError();
            this.showToast('Lỗi lưu tiến trình!', 'error');
        }
    }

    /**
     * Loads snapshot from Slot 1
     */
    loadGame() {
        const savedState = this.storage.loadGameSnapshot(1);
        if (!savedState) {
            this.audio.playError();
            this.showToast('Chưa có bản lưu nào trong Khe 1!', 'error');
            return;
        }

        // Restore resources
        if (savedState.resources) {
            this.economy.food = savedState.resources.food ?? 200;
            this.economy.wood = savedState.resources.wood ?? 150;
            this.economy.stone = savedState.resources.stone ?? 80;
            this.economy.bone = savedState.resources.bone ?? 40;
            this.economy.score = savedState.resources.score ?? 100;
            this.economy.notifyChange();
        }

        // Restore quest
        if (savedState.questStage !== undefined) {
            this.quest.currentStage = savedState.questStage;
            this.quest.completedObjectives.clear();
        }

        // Restore buildings
        if (savedState.buildings) {
            // Free old footprints
            this.world.buildings.forEach(b => {
                this.world.freeFootprint(b.x, b.y, b.width, b.height);
            });
            this.world.buildings = [];

            savedState.buildings.forEach(bData => {
                const def = BUILDING_CATALOG.find(d => d.id === bData.type) || BUILDING_CATALOG[0];
                const b = new BuildingInstance(def, bData.x, bData.y, bData.isConstructed);
                b.hp = bData.hp;
                b.maxHp = bData.maxHp;
                b.level = bData.level;
                b.constructionProgress = bData.constructionProgress;
                this.world.buildings.push(b);
                this.world.occupyFootprint(b.x, b.y, b.width, b.height);
            });
        }

        // Restore villagers
        if (savedState.villagers) {
            this.world.villagers = [];
            savedState.villagers.forEach(vData => {
                const prof = Object.values(PROFESSIONS).find(p => p.id === vData.profession?.id) || PROFESSIONS.VILLAGER;
                const v = new Villager(vData.id, vData.x, vData.y, prof);
                v.hp = vData.hp;
                v.maxHp = vData.maxHp;
                v.state = vData.state;
                v.carriedType = vData.carriedType;
                v.carriedAmount = vData.carriedAmount;
                this.world.villagers.push(v);
            });
        }

        this.audio.playFanfare();
        this.showToast('📂 Tải bản lưu thành công!', 'success');
        this.economy.notifyChange();
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type === 'error' ? 'toast-error' : (type === 'success' ? 'toast-success' : '')}`;
        toast.innerText = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3200);
    }

    handleResize() {
        const wrapper = document.getElementById('viewport-wrapper');
        const rect = wrapper.getBoundingClientRect();
        this.renderer.resize(rect.width, rect.height);
        this.camera.setViewportSize(rect.width, rect.height);
    }

    /**
     * Fixed-timestep Game Loop (60 Hz simulation updates with interpolation)
     */
    gameLoop(timestamp) {
        const elapsed = timestamp - this.lastTime;
        this.lastTime = timestamp;

        // Cap elapsed to avoid spiral of death
        this.accumulator += Math.min(elapsed, 100);

        while (this.accumulator >= this.FIXED_DELTA) {
            this.update(this.FIXED_DELTA);
            this.accumulator -= this.FIXED_DELTA;
        }

        this.render();
        requestAnimationFrame((t) => this.gameLoop(t));
    }

    /**
     * Fixed-frequency simulation step
     */
    update(deltaMs) {
        // Continuous keyboard camera panning
        this.input.update();

        // Smooth camera lerp
        this.camera.update();

        if (this.state === GAME_STATES.PLAYING || this.state === GAME_STATES.BUILDING_PLACEMENT) {
            // Update villagers simulation
            for (const villager of this.world.villagers) {
                villager.update(this.world, this.economy, this.audio);
            }

            // Update economy (food decay)
            this.economy.update(this.world.villagers.length);

            // Periodically evaluate quest objectives
            this.quest.evaluateObjectives(this.world, this.economy, this.audio);
        }
    }

    /**
     * Canvas Render pass
     */
    render() {
        // 1. Clear frame
        this.renderer.clear();

        // 2. Render 96x96 tilemap from maps.json
        this.renderer.renderTilemap(this.world.map, this.camera);

        // 3. Render all world entities sorted by Y depth
        const allEntities = this.world.getAllEntities();
        this.renderer.renderEntities(allEntities, this.camera, this.selectedEntity);

        // 4. Render building placement cursor preview if in placement mode
        if (this.state === GAME_STATES.BUILDING_PLACEMENT && this.placingBuildingDef) {
            const gx = this.input.mouse.gridX;
            const gy = this.input.mouse.gridY;
            const isValid = this.world.canPlaceBuilding(gx, gy, this.placingBuildingDef.width, this.placingBuildingDef.height);
            this.renderer.renderPlacementCursor(this.placingBuildingDef, gx, gy, isValid, this.camera);
        }
    }
}

// Bootstrap application on window load
window.addEventListener('DOMContentLoaded', () => {
    const app = new PrehistoricTribesApp();
    window.gameApp = app; // Expose for verification and headless test inspection
    window.BUILDING_CATALOG = BUILDING_CATALOG;
    app.init().catch(err => {
        console.error('[App] Fatal initialization error:', err);
    });
});
