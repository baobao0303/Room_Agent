/**
 * Renderer Module (web/js/engine/renderer.js)
 * High-performance HTML5 Canvas 2D renderer.
 * Handles staggered isometric tilemap rendering, dual-path sprite blitting (bitmap & vector),
 * and depth-sorted (Y-sorted) entity drawing.
 */

// 14-RGB Palette Table (Byte Table 17 from RECONSTRUCTION_SPEC.md & f.java)
const PALETTE_TABLE_17 = [
    [0, 0, 0],       // 0: Black / Shadow Outline
    [194, 182, 81],  // 1: Pale Gold / Desert Sand
    [167, 150, 63],  // 2: Earth Ochre / Arid Soil
    [180, 166, 71],  // 3: Light Clay
    [102, 81, 31],   // 4: Dark Timber / Bark
    [34, 30, 9],     // 5: Deep Shadow / Charcoal
    [208, 196, 96],  // 6: Thatch / Straw Yellow
    [81, 173, 27],   // 7: Lush Grass Green
    [175, 134, 9],   // 8: Dried Mud / Amber
    [0, 97, 216],    // 9: Deep Water Blue
    [143, 199, 255], // 10: Water Shimmer / Splash White
    [14, 91, 39],    // 11: Deep Jungle Foliage
    [0, 218, 0],     // 12: Bright Canopy Green
    [7, 52, 4]       // 13: Shadow Canopy Dark
];

export class CanvasRenderer {
    constructor(canvas, assetLoader) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d', { alpha: false });
        this.loader = assetLoader;

        // Cache sprite metadata tables
        this.spritesData = assetLoader.getJSON('sprites');
        this.shortTables = this.spritesData?.short_tables || [];
        this.byteTables = this.spritesData?.byte_tables || [];
        this.frames = this.spritesData?.sprite_frames || [];

        // Tile sizing constants
        this.TILE_WIDTH = 22;
        this.TILE_HEIGHT = 16;

        // Offscreen pre-rendered terrain buffer for smooth 60fps rendering
        this.terrainCanvas = null;
        this.terrainCtx = null;
        this.renderedMapIndex = -1;

        // Image rendering config
        this.ctx.imageSmoothingEnabled = false;
    }

    /**
     * Resizes internal canvas dimensions if needed
     */
    resize(width, height) {
        if (this.canvas.width !== width || this.canvas.height !== height) {
            this.canvas.width = width;
            this.canvas.height = height;
            this.ctx.imageSmoothingEnabled = false;
        }
    }

    /**
     * Clears viewport with deep prehistoric background
     */
    clear(bgColor = '#14110d') {
        this.ctx.fillStyle = bgColor;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    /**
     * Slices and renders a single leaf sprite frame according to decompiled f.b()
     * Handles Path A (Bitmap blit) and Path B (Procedural vector primitive)
     */
    drawFrame(frameId, dstX, dstY) {
        if (!frameId || frameId <= 0 || frameId >= this.frames.length) {
            return;
        }

        const f = this.frames[frameId];
        if (!f) return;

        const page = f.page;
        const w = f.width;
        const h = f.height;

        // Target coordinate adjustment from f.java (+11, +8)
        const targetX = Math.floor(dstX + 11);
        const targetY = Math.floor(dstY + 8);

        // Path A: Bitmap Blit from extracted spritesheet (page < 27)
        if (page < 27) {
            const pageName = f.page_name.replace('.png', '');
            const img = this.loader.getImage(pageName);
            if (img && img.complete && img.naturalWidth > 0) {
                this.ctx.drawImage(
                    img,
                    f.atlas_x,
                    f.atlas_y,
                    w,
                    h,
                    targetX,
                    targetY,
                    w,
                    h
                );
            }
            return;
        }

        // Path B: Procedural Vector Drawing Primitives (page >= 27)
        // Bitpacked color index from Byte Table 20 and 21:
        const j20 = this.byteTables[20] ? this.byteTables[20][frameId] : 0;
        const j21 = this.byteTables[21] ? this.byteTables[21][frameId] : 0;
        const colorIdx = (((j20 & 0xFF) >> 5) | ((j21 & 0x80) >> 4)) % 14;
        const rgb = PALETTE_TABLE_17[colorIdx] || [0, 0, 0];
        const colorStyle = `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;

        this.ctx.save();
        this.ctx.fillStyle = colorStyle;
        this.ctx.strokeStyle = colorStyle;

        const j22 = this.byteTables[22] ? this.byteTables[22][frameId] : 0;
        const j23 = this.byteTables[23] ? this.byteTables[23][frameId] : 0;
        const j24 = this.byteTables[24] ? this.byteTables[24][frameId] : 0;

        if (page === 27) {
            // Draw Line
            this.ctx.beginPath();
            this.ctx.moveTo(targetX + (j21 & 0x7F), targetY + j22);
            this.ctx.lineTo(targetX + j23, targetY + j24);
            this.ctx.stroke();
        } else if (page === 28) {
            // Draw Rect Outline
            this.ctx.strokeRect(targetX + (j21 & 0x7F), targetY + j22, j23, j24);
        } else if (page === 29) {
            // Fill Rect
            this.ctx.fillRect(targetX + (j21 & 0x7F) - 11, targetY + j22 - 8, j23, j24);
        } else if (page === 30) {
            // 4x Scaled Fill Rect
            this.ctx.fillRect((targetX + (j21 & 0x7F)) * 4 - 11, (targetY + j22) * 4 - 8, j23 * 4, j24 * 4);
        }

        this.ctx.restore();
    }

    /**
     * Draws composite animations or multi-part structures according to decompiled f.a()
     */
    drawComposite(compositeId, x, y, depth = 0) {
        if (depth > 5 || compositeId <= 0) return;

        const b9 = this.shortTables[9];
        const b10 = this.shortTables[10];
        const j16 = this.byteTables[16];
        const j18 = this.byteTables[18];
        const j19 = this.byteTables[19];

        if (!b9 || !b10 || !j16 || compositeId >= b9.length) {
            // Fallback to leaf draw
            this.drawFrame(compositeId, x, y);
            return;
        }

        const startIndex = b9[compositeId] & 0x1FFF;
        const partCount = j16[compositeId] & 0x3F;

        if (partCount <= 0) {
            this.drawFrame(compositeId, x, y);
            return;
        }

        for (let i = startIndex; i < startIndex + partCount && i < b10.length; i++) {
            const subFrameId = b10[i] & 0x1FFF;
            const shiftX = ((b10[i] & 0xC000) >> 14) << 7;
            const relX = (j18 ? j18[i] : 0) + shiftX;
            const relY = (j19 ? j19[i] : 0);
            const isRecursive = ((b10[i] & 0x2000) >> 13) === 1;

            if (isRecursive) {
                this.drawComposite(subFrameId, x + relX, y + relY, depth + 1);
            } else {
                this.drawFrame(subFrameId, x + relX, y + relY);
            }
        }
    }

    /**
     * Renders visible portion of the 96x96 (or WxH) tilemap within current camera viewport
     */
    renderTilemap(map, camera) {
        if (!map || !map.tiles) return;

        const width = map.width;
        const height = map.height;
        const tiles = map.tiles;

        // Camera viewport in world coordinates
        const viewLeft = camera.x;
        const viewTop = camera.y;
        const viewRight = camera.x + this.canvas.width / camera.zoom;
        const viewBottom = camera.y + this.canvas.height / camera.zoom;

        // Calculate tile bounds to render
        const minTileX = Math.max(0, Math.floor(viewLeft / this.TILE_WIDTH) - 1);
        const maxTileX = Math.min(width - 1, Math.ceil(viewRight / this.TILE_WIDTH) + 1);
        const minTileY = Math.max(0, Math.floor(viewTop / this.TILE_HEIGHT) - 1);
        const maxTileY = Math.min(height - 1, Math.ceil(viewBottom / this.TILE_HEIGHT) + 1);

        this.ctx.save();
        this.ctx.scale(camera.zoom, camera.zoom);
        this.ctx.translate(-camera.x, -camera.y);

        // Render base terrain tiles
        for (let y = minTileY; y <= maxTileY; y++) {
            const row = tiles[y];
            if (!row) continue;
            for (let x = minTileX; x <= maxTileX; x++) {
                const tileId = row[x];
                const screenX = x * this.TILE_WIDTH;
                const screenY = y * this.TILE_HEIGHT;

                if (tileId < 175) {
                    // Normal terrain composite/frame
                    this.drawComposite(tileId, screenX, screenY);
                } else {
                    // Natural obstacle / tree / boulder frame
                    this.drawFrame(tileId, screenX, screenY);
                }
            }
        }

        this.ctx.restore();
    }

    /**
     * Renders a building placement preview with color-coded valid/invalid footprint tiles
     */
    renderPlacementCursor(buildingDef, gridX, gridY, isValid, camera) {
        if (!buildingDef) return;

        this.ctx.save();
        this.ctx.scale(camera.zoom, camera.zoom);
        this.ctx.translate(-camera.x, -camera.y);

        const w = buildingDef.width * this.TILE_WIDTH;
        const h = buildingDef.height * this.TILE_HEIGHT;
        const posX = gridX * this.TILE_WIDTH;
        const posY = gridY * this.TILE_HEIGHT;

        // Footprint rectangle
        this.ctx.fillStyle = isValid ? 'rgba(46, 204, 113, 0.4)' : 'rgba(231, 76, 60, 0.45)';
        this.ctx.strokeStyle = isValid ? '#2ecc71' : '#e74c3c';
        this.ctx.lineWidth = 1.5;

        this.ctx.fillRect(posX, posY, w, h);
        this.ctx.strokeRect(posX, posY, w, h);

        // Tile subdivisions
        this.ctx.strokeStyle = isValid ? 'rgba(46, 204, 113, 0.6)' : 'rgba(231, 76, 60, 0.6)';
        this.ctx.lineWidth = 0.5;
        for (let dx = 0; dx < buildingDef.width; dx++) {
            for (let dy = 0; dy < buildingDef.height; dy++) {
                this.ctx.strokeRect(
                    posX + dx * this.TILE_WIDTH,
                    posY + dy * this.TILE_HEIGHT,
                    this.TILE_WIDTH,
                    this.TILE_HEIGHT
                );
            }
        }

        // Draw preview of building icon or frame
        if (buildingDef.spriteFrameId) {
            this.ctx.globalAlpha = 0.75;
            this.drawFrame(buildingDef.spriteFrameId, posX, posY);
            this.ctx.globalAlpha = 1.0;
        }

        this.ctx.restore();
    }

    /**
     * Renders all active world entities (villagers, buildings, animals, resources)
     * using strict Y-sorting for proper isometric visual depth.
     */
    renderEntities(entities, camera, selectedEntity = null) {
        if (!entities || entities.length === 0) return;

        // Filter entities within viewport range
        const viewLeft = camera.x - 64;
        const viewTop = camera.y - 64;
        const viewRight = camera.x + this.canvas.width / camera.zoom + 64;
        const viewBottom = camera.y + this.canvas.height / camera.zoom + 64;

        const visibleEntities = entities.filter(e => {
            const px = e.worldX !== undefined ? e.worldX : e.x * this.TILE_WIDTH;
            const py = e.worldY !== undefined ? e.worldY : e.y * this.TILE_HEIGHT;
            return px >= viewLeft && px <= viewRight && py >= viewTop && py <= viewBottom;
        });

        // Depth sort: ascending order of sortKey (Y coordinate + subtle Z bias)
        visibleEntities.sort((a, b) => {
            const yA = (a.worldY !== undefined ? a.worldY : a.y * this.TILE_HEIGHT) + (a.sortBias || 0);
            const yB = (b.worldY !== undefined ? b.worldY : b.y * this.TILE_HEIGHT) + (b.sortBias || 0);
            return yA - yB;
        });

        this.ctx.save();
        this.ctx.scale(camera.zoom, camera.zoom);
        this.ctx.translate(-camera.x, -camera.y);

        for (const entity of visibleEntities) {
            entity.render(this, selectedEntity === entity);
        }

        this.ctx.restore();
    }

    /**
     * Utility to draw overhead health bar
     */
    drawHealthBar(x, y, currentHp, maxHp, width = 24, height = 3) {
        if (maxHp <= 0) return;
        const pct = Math.max(0, Math.min(1, currentHp / maxHp));

        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(x - width / 2, y, width, height);

        this.ctx.fillStyle = pct > 0.5 ? '#2ecc71' : (pct > 0.25 ? '#f39c12' : '#e74c3c');
        this.ctx.fillRect(x - width / 2, y, width * pct, height);

        this.ctx.strokeStyle = '#000';
        this.ctx.lineWidth = 0.5;
        this.ctx.strokeRect(x - width / 2, y, width, height);
    }

    /**
     * Utility to draw entity selection ring
     */
    drawSelectionRing(x, y, radius = 12) {
        this.ctx.save();
        this.ctx.strokeStyle = '#f5b041';
        this.ctx.lineWidth = 1.5;
        this.ctx.setLineDash([3, 2]);

        this.ctx.beginPath();
        this.ctx.ellipse(x, y, radius, radius * 0.55, 0, 0, Math.PI * 2);
        this.ctx.stroke();
        this.ctx.restore();
    }
}
