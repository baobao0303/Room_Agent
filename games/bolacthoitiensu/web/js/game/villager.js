/**
 * Villager Module (web/js/game/villager.js)
 * Implements the 100-unit simulation with 8-state AI FSM, profession roles,
 * sub-tile path movement, carried resource visualization, and job assignment.
 */

export const VILLAGER_STATES = {
    IDLE: 0,
    WALK: 1,
    REST: 28,
    GATHER: 44,
    BUILD: 55,
    DEPOSIT: 59,
    TRAIN: 69,
    FIGHT: 87
};

export const PROFESSIONS = {
    VILLAGER: { id: 0, name: 'Dân làng (Hái lượm)', icon: '🧺', targetResourceType: 0 }, // Food
    WOODCUTTER: { id: 1, name: 'Thợ đốn củi', icon: '🪓', targetResourceType: 1 },        // Wood
    MINER: { id: 2, name: 'Thợ mỏ (Khai thác)', icon: '⛏️', targetResourceType: 2 },        // Stone
    HUNTER: { id: 3, name: 'Thợ săn (Săn thú)', icon: '🏹', targetResourceType: 3 },       // Bone & Meat
    BUILDER: { id: 4, name: 'Thợ xây dựng', icon: '🔨', targetResourceType: null },
    WARRIOR: { id: 5, name: 'Chiến binh', icon: '⚔️', targetResourceType: null }
};

export class Villager {
    constructor(id, gridX, gridY, profession = PROFESSIONS.VILLAGER) {
        this.id = id;
        this.name = `Dân làng #${id}`;
        this.x = gridX;
        this.y = gridY;
        this.dx = 0; // sub-tile fine offset (-11..+11)
        this.dy = 0; // sub-tile fine offset (-8..+8)
        this.dir = 4; // 0..7 (N, NE, E, SE, S, SW, W, NW)

        this.hp = 100;
        this.maxHp = 100;
        this.stamina = 100;
        this.maxStamina = 100;

        this.profession = profession;
        this.state = VILLAGER_STATES.IDLE;

        // Pathfinding waypoints
        this.path = [];
        this.targetGridX = gridX;
        this.targetGridY = gridY;
        this.targetEntity = null;

        // Inventory
        this.carriedType = null; // 0: Food, 1: Wood, 2: Stone, 3: Bone
        this.carriedAmount = 0;
        this.maxCarry = 15;

        // Animation / Action ticker
        this.actionTimer = 0;
        this.moveSpeed = 1.0; // grid tiles per second

        // Faction allegiance (0: Player tribe, 1: Neutral, 2: Hostile)
        this.allegiance = 0;
        this.sortBias = 10;
    }

    /**
     * Assigns a new job role and resets active state to seek new task
     */
    assignJob(profession) {
        this.profession = profession;
        this.carriedAmount = 0;
        this.carriedType = null;
        this.path = [];
        this.targetEntity = null;
        this.state = VILLAGER_STATES.IDLE;
    }

    /**
     * Orders villager to move directly to a specific target tile
     */
    moveTo(world, targetX, targetY) {
        const path = world.findPath(this.x, this.y, targetX, targetY);
        if (path.length > 0) {
            this.path = path;
            this.targetGridX = targetX;
            this.targetGridY = targetY;
            this.state = VILLAGER_STATES.WALK;
        }
    }

    /**
     * 60 Hz Simulation Tick
     */
    update(world, economy, audio) {
        // Decrease stamina slightly while working
        if (this.state !== VILLAGER_STATES.REST && this.state !== VILLAGER_STATES.IDLE) {
            this.stamina = Math.max(0, this.stamina - 0.02);
            if (this.stamina <= 5 && this.state !== VILLAGER_STATES.DEPOSIT) {
                // Exhausted: seek nearest Tent to rest
                const tent = world.findNearestBuilding(this.x, this.y, 2); // Tent ID 2
                if (tent) {
                    this.moveTo(world, tent.x + 1, tent.y + 1);
                    this.state = VILLAGER_STATES.REST;
                    return;
                }
            }
        }

        switch (this.state) {
            case VILLAGER_STATES.IDLE:
                this.handleIdleState(world);
                break;

            case VILLAGER_STATES.WALK:
                this.handleWalkState(world);
                break;

            case VILLAGER_STATES.GATHER:
                this.handleGatherState(world, economy, audio);
                break;

            case VILLAGER_STATES.BUILD:
                this.handleBuildState(world, audio);
                break;

            case VILLAGER_STATES.DEPOSIT:
                this.handleDepositState(world, economy, audio);
                break;

            case VILLAGER_STATES.REST:
                this.handleRestState(world);
                break;
        }
    }

    handleIdleState(world) {
        // Look for work depending on profession
        if (this.profession.id === PROFESSIONS.BUILDER.id) {
            const unfinished = world.findUnfinishedBuilding(this.x, this.y);
            if (unfinished) {
                this.targetEntity = unfinished;
                this.moveTo(world, unfinished.x + 1, unfinished.y + 1);
                return;
            }
        } else if (this.profession.targetResourceType !== null && this.profession.targetResourceType !== undefined) {
            const resNode = world.findNearestResource(this.x, this.y, this.profession.targetResourceType);
            if (resNode) {
                this.targetEntity = resNode;
                this.moveTo(world, resNode.x, resNode.y);
                return;
            }
        }

        // Wander slightly around village center if idle
        this.actionTimer++;
        if (this.actionTimer > 180) { // every 3 seconds
            this.actionTimer = 0;
            const wanderX = Math.max(2, Math.min(world.width - 3, this.x + Math.floor(Math.random() * 5) - 2));
            const wanderY = Math.max(2, Math.min(world.height - 3, this.y + Math.floor(Math.random() * 5) - 2));
            if (world.isWalkable(wanderX, wanderY)) {
                this.moveTo(world, wanderX, wanderY);
            }
        }
    }

    handleWalkState(world) {
        if (this.path.length === 0) {
            // Arrived at destination
            if (this.targetEntity) {
                if (this.targetEntity.type !== undefined && this.targetEntity.amount !== undefined) {
                    // Resource node reached
                    this.state = VILLAGER_STATES.GATHER;
                } else if (this.targetEntity.isConstructed !== undefined && !this.targetEntity.isConstructed) {
                    // Building site reached
                    this.state = VILLAGER_STATES.BUILD;
                } else if (this.targetEntity.type === 6) { // Warehouse
                    this.state = VILLAGER_STATES.DEPOSIT;
                }
            } else {
                this.state = VILLAGER_STATES.IDLE;
            }
            return;
        }

        const nextWaypoint = this.path[0];
        const step = 0.08; // movement per tick

        const dx = nextWaypoint.x - this.x;
        const dy = nextWaypoint.y - this.y;
        const dist = Math.hypot(dx, dy);

        if (dist <= step) {
            this.x = nextWaypoint.x;
            this.y = nextWaypoint.y;
            this.path.shift(); // Next waypoint
        } else {
            this.x += (dx / dist) * step;
            this.y += (dy / dist) * step;

            // Update facing direction
            if (Math.abs(dx) > Math.abs(dy)) {
                this.dir = dx > 0 ? 2 : 6; // East or West
            } else {
                this.dir = dy > 0 ? 4 : 0; // South or North
            }
        }
    }

    handleGatherState(world, economy, audio) {
        if (!this.targetEntity || this.targetEntity.amount <= 0) {
            // Node depleted, return to deposit or seek new node
            if (this.carriedAmount > 0) {
                const wh = world.findNearestBuilding(this.x, this.y, 6); // Warehouse
                if (wh) {
                    this.targetEntity = wh;
                    this.moveTo(world, wh.x + 1, wh.y + 1);
                } else {
                    this.state = VILLAGER_STATES.IDLE;
                }
            } else {
                this.targetEntity = null;
                this.state = VILLAGER_STATES.IDLE;
            }
            return;
        }

        this.actionTimer++;
        if (this.actionTimer >= 20) { // gather tick (~0.33s)
            this.actionTimer = 0;
            const yieldAmount = Math.min(2, this.targetEntity.amount);
            this.targetEntity.amount -= yieldAmount;
            this.carriedType = this.targetEntity.type;
            this.carriedAmount += yieldAmount;

            if (audio && Math.random() < 0.3) {
                audio.playGather();
            }

            if (this.carriedAmount >= this.maxCarry || this.targetEntity.amount <= 0) {
                // Carry full, seek warehouse
                const wh = world.findNearestBuilding(this.x, this.y, 6);
                if (wh) {
                    this.targetEntity = wh;
                    this.moveTo(world, wh.x + 1, wh.y + 1);
                } else {
                    // Fallback to village chief tent if no warehouse built yet
                    const chief = world.findNearestBuilding(this.x, this.y, 3);
                    if (chief) {
                        this.targetEntity = chief;
                        this.moveTo(world, chief.x + 1, chief.y + 1);
                    } else {
                        // Immediately deposit if nowhere to go
                        economy.deposit(this.carriedType, this.carriedAmount);
                        this.carriedAmount = 0;
                        this.state = VILLAGER_STATES.IDLE;
                    }
                }
            }
        }
    }

    handleBuildState(world, audio) {
        if (!this.targetEntity || this.targetEntity.isConstructed) {
            // Building finished, look for another or idle
            this.targetEntity = null;
            this.state = VILLAGER_STATES.IDLE;
            return;
        }

        this.actionTimer++;
        if (this.actionTimer >= 25) {
            this.actionTimer = 0;
            this.targetEntity.addConstructionWork(4);
            if (audio && Math.random() < 0.4) {
                audio.playBuild();
            }

            if (this.targetEntity.isConstructed) {
                if (audio) audio.playFanfare();
                this.targetEntity = null;
                this.state = VILLAGER_STATES.IDLE;
            }
        }
    }

    handleDepositState(world, economy, audio) {
        if (this.carriedAmount > 0) {
            economy.deposit(this.carriedType, this.carriedAmount);
            if (audio) audio.playClick();
            this.carriedAmount = 0;
            this.carriedType = null;
        }

        // Resume prior profession job
        this.state = VILLAGER_STATES.IDLE;
    }

    handleRestState(world) {
        this.stamina = Math.min(this.maxStamina, this.stamina + 0.3);
        this.hp = Math.min(this.maxHp, this.hp + 0.1);

        if (this.stamina >= this.maxStamina) {
            this.state = VILLAGER_STATES.IDLE;
        }
    }

    /**
     * Renders villager on canvas
     */
    render(renderer, isSelected = false) {
        const posX = Math.floor(this.x * 22);
        const posY = Math.floor(this.y * 16);
        const ctx = renderer.ctx;

        // Draw shadow ellipse under feet
        ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
        ctx.beginPath();
        ctx.ellipse(posX + 11, posY + 14, 7, 3.5, 0, 0, Math.PI * 2);
        ctx.fill();

        // Draw villager body / sprite
        // Authentic prehistoric villager representation:
        // Use composite/frame from pi0_01 or fallback pixel character
        renderer.drawFrame(259, posX, posY);

        // Draw job tool / profession badge
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';

        // Carried resource visualization above head
        if (this.carriedAmount > 0) {
            const icons = ['🍖', '🪵', '🪨', '🦴'];
            const resIcon = icons[this.carriedType] || '📦';

            ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
            ctx.fillRect(posX + 2, posY - 14, 18, 12);
            ctx.strokeStyle = '#f5b041';
            ctx.lineWidth = 0.5;
            ctx.strokeRect(posX + 2, posY - 14, 18, 12);

            ctx.fillText(resIcon, posX + 11, posY - 4);
        }

        // Selection highlight ring
        if (isSelected) {
            renderer.drawSelectionRing(posX + 11, posY + 10, 10);
            renderer.drawHealthBar(posX + 11, posY - 6, this.hp, this.maxHp, 20);
        }
    }
}
