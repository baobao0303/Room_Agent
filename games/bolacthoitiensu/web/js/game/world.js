/**
 * World Module (web/js/game/world.js)
 * Manages world terrain grid, collision matrix, entities list, spatial queries, and grid pathfinding.
 */

export class WorldGrid {
    constructor(mapsData) {
        this.mapsData = mapsData;
        this.levelIndex = 0;
        this.map = null;

        this.width = 96;
        this.height = 96;
        this.TILE_WIDTH = 22;
        this.TILE_HEIGHT = 16;

        // Collision Grid: 0 = walkable, -126 = boundary, -125 = water, -124 = obstacle/building
        this.collision = [];

        // Entity Collections
        this.villagers = [];
        this.buildings = [];
        this.resources = [];
        this.animals = [];

        // Load default map 0 (or 5 for 96x96 full world)
        this.loadLevel(0);
    }

    /**
     * Loads level map and initializes collision grid
     */
    loadLevel(levelIndex = 0) {
        this.levelIndex = levelIndex;
        const maps = this.mapsData?.maps || [];
        // Map 0 is Level 0 (64x48) or Map 5 (96x96)
        this.map = maps[levelIndex] || maps[0];

        if (!this.map) {
            console.error(`[World] Map at level ${levelIndex} not found!`);
            return;
        }

        this.width = this.map.width;
        this.height = this.map.height;

        // Clone collision matrix from maps.json
        this.collision = [];
        for (let y = 0; y < this.height; y++) {
            const row = [];
            const srcRow = this.map.collision[y] || [];
            for (let x = 0; x < this.width; x++) {
                row.push(srcRow[x] !== undefined ? srcRow[x] : 0);
            }
            this.collision.push(row);
        }

        // Initialize natural resource nodes from map obstacles or standard prehistoric spawn clusters
        this.initNaturalResources();
    }

    /**
     * Spawns natural resource nodes (Trees, Boulders, Berry Bushes, Mammoths)
     */
    initNaturalResources() {
        this.resources = [];

        // Scan map for obstacle tiles (-124) or seed natural resource clusters around center
        const centerX = Math.floor(this.width / 2);
        const centerY = Math.floor(this.height / 2);

        // 1. Wood trees (cluster east and west)
        for (let i = 0; i < 28; i++) {
            const rx = Math.max(2, Math.min(this.width - 3, centerX + (i % 2 === 0 ? 8 : -8) + Math.floor(i / 2) % 6));
            const ry = Math.max(2, Math.min(this.height - 3, centerY - 10 + Math.floor(i * 1.3) % 20));
            if (this.isWalkable(rx, ry)) {
                this.resources.push({
                    id: `tree_${i}`,
                    type: 1, // 1 = Wood
                    name: 'Cây cổ thụ',
                    x: rx,
                    y: ry,
                    amount: 120,
                    maxAmount: 120,
                    spriteFrameId: 181, // Prehistoric tree/flora
                    render(renderer) {
                        renderer.drawFrame(181, this.x * 22, this.y * 16 - 8);
                    }
                });
                this.collision[ry][rx] = -124;
            }
        }

        // 2. Stone quarries / Boulders (cluster north)
        for (let i = 0; i < 16; i++) {
            const rx = Math.max(2, Math.min(this.width - 3, centerX - 12 + (i % 8) * 3));
            const ry = Math.max(2, Math.min(this.height - 3, centerY - 14 + Math.floor(i / 8) * 3));
            if (this.isWalkable(rx, ry)) {
                this.resources.push({
                    id: `stone_${i}`,
                    type: 2, // 2 = Stone
                    name: 'Mỏ đá tiền sử',
                    x: rx,
                    y: ry,
                    amount: 150,
                    maxAmount: 150,
                    spriteFrameId: 182,
                    render(renderer) {
                        renderer.drawFrame(182, this.x * 22, this.y * 16);
                    }
                });
                this.collision[ry][rx] = -124;
            }
        }

        // 3. Berry bushes (cluster south)
        for (let i = 0; i < 18; i++) {
            const rx = Math.max(2, Math.min(this.width - 3, centerX - 8 + (i % 6) * 3));
            const ry = Math.max(2, Math.min(this.height - 3, centerY + 10 + Math.floor(i / 6) * 3));
            if (this.isWalkable(rx, ry)) {
                this.resources.push({
                    id: `food_${i}`,
                    type: 0, // 0 = Food
                    name: 'Bụi quả dại',
                    x: rx,
                    y: ry,
                    amount: 80,
                    maxAmount: 80,
                    spriteFrameId: 11,
                    render(renderer) {
                        renderer.drawFrame(11, this.x * 22, this.y * 16);
                    }
                });
                this.collision[ry][rx] = -124;
            }
        }

        // 4. Large Mammoth Carcasses / Hunting Game (for Bone & Meat)
        for (let i = 0; i < 6; i++) {
            const rx = Math.max(2, Math.min(this.width - 3, centerX + 14 + (i % 3) * 4));
            const ry = Math.max(2, Math.min(this.height - 3, centerY + 6 + Math.floor(i / 3) * 5));
            if (this.isWalkable(rx, ry)) {
                this.resources.push({
                    id: `mammoth_${i}`,
                    type: 3, // 3 = Bone
                    name: 'Xác Voi Mamut',
                    x: rx,
                    y: ry,
                    amount: 100,
                    maxAmount: 100,
                    spriteFrameId: 1708,
                    render(renderer) {
                        renderer.drawFrame(1708, this.x * 22, this.y * 16 - 12);
                    }
                });
                this.collision[ry][rx] = -124;
            }
        }
    }

    /**
     * Checks if a grid coordinate is within world boundaries and walkable
     */
    isWalkable(gx, gy) {
        if (gx < 0 || gx >= this.width || gy < 0 || gy >= this.height) {
            return false;
        }
        return this.collision[gy][gx] === 0;
    }

    /**
     * Checks if a rectangular footprint is completely walkable and inside bounds
     */
    canPlaceBuilding(gx, gy, width, height) {
        if (gx < 1 || gy < 1 || gx + width >= this.width - 1 || gy + height >= this.height - 1) {
            return false;
        }

        for (let dy = 0; dy < height; dy++) {
            for (let dx = 0; dx < width; dx++) {
                const cell = this.collision[gy + dy][gx + dx];
                if (cell !== 0) {
                    return false;
                }
            }
        }
        return true;
    }

    /**
     * Marks building footprint as occupied (-124) in collision grid
     */
    occupyFootprint(gx, gy, width, height, val = -124) {
        for (let dy = 0; dy < height; dy++) {
            for (let dx = 0; dx < width; dx++) {
                if (gy + dy < this.height && gx + dx < this.width) {
                    this.collision[gy + dy][gx + dx] = val;
                }
            }
        }
    }

    /**
     * Frees building footprint back to 0 (walkable)
     */
    freeFootprint(gx, gy, width, height) {
        this.occupyFootprint(gx, gy, width, height, 0);
    }

    /**
     * Spatial query: finds any entity (villager, building, or resource) at grid position
     */
    getEntityAt(gx, gy) {
        // 1. Check villagers first (highest click priority)
        for (const v of this.villagers) {
            const vGx = Math.floor(v.x);
            const vGy = Math.floor(v.y);
            if (vGx === gx && vGy === gy) {
                return v;
            }
        }

        // 2. Check buildings
        for (const b of this.buildings) {
            if (gx >= b.x && gx < b.x + b.width && gy >= b.y && gy < b.y + b.height) {
                return b;
            }
        }

        // 3. Check natural resources
        for (const r of this.resources) {
            if (r.x === gx && r.y === gy) {
                return r;
            }
        }

        return null;
    }

    /**
     * Finds nearest building of type (e.g. Warehouse ID 6, Chief Tent ID 3, Tent ID 2)
     */
    findNearestBuilding(gx, gy, buildingTypeId = null) {
        let bestDist = Infinity;
        let bestBuilding = null;

        for (const b of this.buildings) {
            if (buildingTypeId !== null && b.type !== buildingTypeId) continue;
            // Center of building
            const bcx = b.x + b.width / 2;
            const bcy = b.y + b.height / 2;
            const dist = Math.hypot(bcx - gx, bcy - gy);
            if (dist < bestDist) {
                bestDist = dist;
                bestBuilding = b;
            }
        }
        return bestBuilding;
    }

    /**
     * Finds nearest active resource node of requested type (0: Food, 1: Wood, 2: Stone, 3: Bone)
     */
    findNearestResource(gx, gy, resourceType) {
        let bestDist = Infinity;
        let bestNode = null;

        for (const r of this.resources) {
            if (r.type !== resourceType || r.amount <= 0) continue;
            const dist = Math.hypot(r.x - gx, r.y - gy);
            if (dist < bestDist) {
                bestDist = dist;
                bestNode = r;
            }
        }
        return bestNode;
    }

    /**
     * Finds nearest building currently under construction that needs builder workers
     */
    findUnfinishedBuilding(gx, gy) {
        let bestDist = Infinity;
        let bestBuilding = null;

        for (const b of this.buildings) {
            if (!b.isConstructed || b.hp < b.maxHp) {
                const bcx = b.x + b.width / 2;
                const bcy = b.y + b.height / 2;
                const dist = Math.hypot(bcx - gx, bcy - gy);
                if (dist < bestDist) {
                    bestDist = dist;
                    bestBuilding = b;
                }
            }
        }
        return bestBuilding;
    }

    /**
     * Breadth-First-Search (BFS) Pathfinding on 2D walkable grid.
     * Returns an array of {x, y} waypoints from start to target.
     */
    findPath(startX, startY, targetX, targetY, maxRange = 50) {
        startX = Math.floor(startX);
        startY = Math.floor(startY);
        targetX = Math.floor(targetX);
        targetY = Math.floor(targetY);

        if (startX === targetX && startY === targetY) {
            return [];
        }

        // If target is blocked (e.g. building footprint or resource tree), find the nearest adjacent walkable cell
        if (!this.isWalkable(targetX, targetY)) {
            const adjacents = [
                { x: targetX + 1, y: targetY },
                { x: targetX - 1, y: targetY },
                { x: targetX, y: targetY + 1 },
                { x: targetX, y: targetY - 1 },
                { x: targetX + 1, y: targetY + 1 },
                { x: targetX - 1, y: targetY + 1 },
                { x: targetX + 1, y: targetY - 1 },
                { x: targetX - 1, y: targetY - 1 }
            ].filter(cell => this.isWalkable(cell.x, cell.y));

            if (adjacents.length === 0) return [];
            // Pick closest to start
            adjacents.sort((a, b) => Math.hypot(a.x - startX, a.y - startY) - Math.hypot(b.x - startX, b.y - startY));
            targetX = adjacents[0].x;
            targetY = adjacents[0].y;
        }

        const queue = [{ x: startX, y: startY }];
        const visited = new Set([`${startX},${startY}`]);
        const parent = new Map();

        const dirs = [
            { dx: 1, dy: 0 },
            { dx: -1, dy: 0 },
            { dx: 0, dy: 1 },
            { dx: 0, dy: -1 },
            { dx: 1, dy: 1 },
            { dx: -1, dy: 1 },
            { dx: 1, dy: -1 },
            { dx: -1, dy: -1 }
        ];

        let found = false;
        let steps = 0;

        while (queue.length > 0 && steps < 2000) {
            steps++;
            const current = queue.shift();

            if (current.x === targetX && current.y === targetY) {
                found = true;
                break;
            }

            for (const d of dirs) {
                const nx = current.x + d.dx;
                const ny = current.y + d.dy;
                const key = `${nx},${ny}`;

                if (nx >= 0 && nx < this.width && ny >= 0 && ny < this.height) {
                    if (!visited.has(key) && this.isWalkable(nx, ny)) {
                        visited.add(key);
                        parent.set(key, current);
                        queue.push({ x: nx, y: ny });
                    }
                }
            }
        }

        if (!found) return [];

        // Reconstruct path
        const path = [];
        let currKey = `${targetX},${targetY}`;
        while (currKey !== `${startX},${startY}`) {
            const p = parent.get(currKey);
            if (!p) break;
            const [cx, cy] = currKey.split(',').map(Number);
            path.unshift({ x: cx, y: cy });
            currKey = `${p.x},${p.y}`;
        }

        return path;
    }

    /**
     * Returns a flat list of all renderable entities for Y-sorting
     */
    getAllEntities() {
        return [
            ...this.resources,
            ...this.buildings,
            ...this.villagers,
            ...this.animals
        ];
    }
}
