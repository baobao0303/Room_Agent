/**
 * Loader Module (web/js/engine/loader.js)
 * Asynchronously loads and caches JSON datasets and PNG spritesheets.
 */

export class AssetLoader {
    constructor() {
        this.data = new Map();
        this.images = new Map();
        this.loadedCount = 0;
        this.totalCount = 0;
    }

    /**
     * Load a JSON file by relative or absolute URL
     */
    async loadJSON(key, url) {
        try {
            const resp = await fetch(url);
            if (!resp.ok) {
                throw new Error(`HTTP ${resp.status} while fetching JSON: ${url}`);
            }
            const json = await resp.json();
            this.data.set(key, json);
            return json;
        } catch (err) {
            console.error(`[Loader] Failed to load JSON '${key}' from ${url}:`, err);
            throw err;
        }
    }

    /**
     * Load an Image element by URL
     */
    loadImage(key, url) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = 'anonymous';
            img.onload = () => {
                this.images.set(key, img);
                resolve(img);
            };
            img.onerror = (e) => {
                console.warn(`[Loader] Failed to load image '${key}' from ${url}`, e);
                // We resolve anyway with an empty placeholder image so game doesn't crash on missing optional sheets
                this.images.set(key, img);
                resolve(img);
            };
            img.src = url;
        });
    }

    /**
     * Preloads all required datasets and core sprite sheets
     */
    async preloadAll(onProgress = () => {}) {
        // 1. Data JSONs
        const jsonFiles = [
            { key: 'maps', url: 'data/maps.json' },
            { key: 'sprites', url: 'data/sprites_pd0.json' },
            { key: 'config', url: 'data/config_a.json' },
            { key: 'localization', url: 'data/localization_vi.json' },
            { key: 'audio', url: 'data/audio_sa.json' }
        ];

        // 2. Sprite sheets
        const imageFiles = [];

        // pi0_00 to pi0_26
        for (let i = 0; i <= 26; i++) {
            const pad = i.toString().padStart(2, '0');
            imageFiles.push({ key: `pi0_${pad}`, url: `sprites/pi0_${pad}.png` });
        }

        // Portraits pi9_00 to pi9_05
        for (let i = 0; i <= 5; i++) {
            const pad = i.toString().padStart(2, '0');
            imageFiles.push({ key: `pi9_${pad}`, url: `sprites/pi9_${pad}.png` });
        }

        // Backgrounds & titles l0 to l3
        ['l0', 'l1', 'l2', 'l3'].forEach(name => {
            imageFiles.push({ key: name, url: `sprites/${name}.png` });
        });

        // Background terrains pi8_00 to pi8_11
        for (let i = 0; i <= 11; i++) {
            const pad = i.toString().padStart(2, '0');
            imageFiles.push({ key: `pi8_${pad}`, url: `sprites/pi8_${pad}.png` });
        }

        this.totalCount = jsonFiles.length + imageFiles.length;
        this.loadedCount = 0;

        const reportProgress = () => {
            this.loadedCount++;
            onProgress(this.loadedCount, this.totalCount);
        };

        // Load JSON files first
        await Promise.all(jsonFiles.map(async item => {
            await this.loadJSON(item.key, item.url);
            reportProgress();
        }));

        // Load image files
        await Promise.all(imageFiles.map(async item => {
            await this.loadImage(item.key, item.url);
            reportProgress();
        }));

        console.log(`[Loader] Successfully loaded ${this.data.size} data files and ${this.images.size} sprite images.`);
        return { data: this.data, images: this.images };
    }

    getJSON(key) {
        return this.data.get(key);
    }

    getImage(key) {
        return this.images.get(key);
    }
}
