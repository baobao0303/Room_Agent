/**
 * Storage Module (web/js/engine/storage.js)
 * Emulates J2ME MIDP RecordStore RMS persistence using localStorage.
 * Slot 0: User options & audio settings.
 * Slot 1: Primary game state & world snapshot.
 * Slot 2: Secondary / autosave snapshot.
 */

export class GameStorage {
    constructor() {
        this.PREFIX = 'prehistoric_tribes_';
    }

    /**
     * Checks if localStorage is available in browser environment
     */
    isAvailable() {
        try {
            const testKey = '__tribes_test__';
            localStorage.setItem(testKey, testKey);
            localStorage.removeItem(testKey);
            return true;
        } catch (e) {
            console.warn('[Storage] LocalStorage is not available:', e);
            return false;
        }
    }

    /**
     * Loads Slot 0 configuration (sound, volume, language, highest level)
     */
    loadSlot0() {
        const defaultCfg = {
            version: '0.1.28',
            score: 0,
            soundEnabled: true,
            musicVolume: 8,
            sfxVolume: 8,
            unlockedLevel: 0,
            language: 'vi',
            vibration: 1
        };

        if (!this.isAvailable()) return defaultCfg;

        try {
            const raw = localStorage.getItem(`${this.PREFIX}slot0`);
            if (!raw) return defaultCfg;
            const parsed = JSON.parse(raw);
            return { ...defaultCfg, ...parsed };
        } catch (err) {
            console.warn('[Storage] Error loading slot 0, falling back to defaults:', err);
            return defaultCfg;
        }
    }

    /**
     * Saves Slot 0 configuration
     */
    saveSlot0(cfg) {
        if (!this.isAvailable()) return false;
        try {
            localStorage.setItem(`${this.PREFIX}slot0`, JSON.stringify(cfg));
            return true;
        } catch (err) {
            console.warn('[Storage] Error saving slot 0:', err);
            return false;
        }
    }

    /**
     * Loads a game state snapshot from slot 1 or 2
     */
    loadGameSnapshot(slotId = 1) {
        if (!this.isAvailable()) return null;

        try {
            const raw = localStorage.getItem(`${this.PREFIX}slot${slotId}`);
            if (!raw) return null;
            const state = JSON.parse(raw);
            console.log(`[Storage] Successfully loaded savegame from Slot ${slotId}`);
            return state;
        } catch (err) {
            console.warn(`[Storage] Failed to parse savegame from Slot ${slotId}:`, err);
            return null;
        }
    }

    /**
     * Serializes and saves current game state into slot 1 or 2
     */
    saveGameSnapshot(slotId = 1, gameState) {
        if (!this.isAvailable() || !gameState) return false;

        try {
            const payload = {
                version: '0.1.28',
                timestamp: Date.now(),
                levelIndex: gameState.levelIndex ?? 0,
                questStage: gameState.questStage ?? 0,
                difficulty: gameState.difficulty ?? 1,
                resources: {
                    food: gameState.resources?.food ?? 200,
                    wood: gameState.resources?.wood ?? 150,
                    stone: gameState.resources?.stone ?? 80,
                    bone: gameState.resources?.bone ?? 40,
                    score: gameState.resources?.score ?? 0
                },
                villagers: (gameState.villagers || []).map(v => ({
                    id: v.id,
                    x: v.x,
                    y: v.y,
                    dx: v.dx || 0,
                    dy: v.dy || 0,
                    dir: v.dir || 0,
                    hp: v.hp,
                    maxHp: v.maxHp,
                    profession: v.profession,
                    state: v.state,
                    targetX: v.targetX,
                    targetY: v.targetY,
                    carriedType: v.carriedType,
                    carriedAmount: v.carriedAmount,
                    allegiance: v.allegiance
                })),
                buildings: (gameState.buildings || []).map(b => ({
                    id: b.id,
                    x: b.x,
                    y: b.y,
                    width: b.width,
                    height: b.height,
                    type: b.type,
                    hp: b.hp,
                    maxHp: b.maxHp,
                    level: b.level || 1,
                    constructionProgress: b.constructionProgress ?? 100,
                    isConstructed: b.isConstructed ?? true
                })),
                questObjectives: gameState.questObjectives || {}
            };

            localStorage.setItem(`${this.PREFIX}slot${slotId}`, JSON.stringify(payload));
            console.log(`[Storage] Successfully saved game state to Slot ${slotId}`);
            return true;
        } catch (err) {
            console.warn(`[Storage] Failed to save game state to Slot ${slotId}:`, err);
            return false;
        }
    }

    /**
     * Checks if a save exists in a slot
     */
    hasSave(slotId = 1) {
        if (!this.isAvailable()) return false;
        return localStorage.getItem(`${this.PREFIX}slot${slotId}`) !== null;
    }

    /**
     * Deletes a save in a slot
     */
    deleteSave(slotId = 1) {
        if (!this.isAvailable()) return;
        localStorage.removeItem(`${this.PREFIX}slot${slotId}`);
    }
}
