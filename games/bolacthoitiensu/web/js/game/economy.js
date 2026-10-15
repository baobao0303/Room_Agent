/**
 * Economy Module (web/js/game/economy.js)
 * Manages tribe stockpiles (Food, Wood, Stone, Bone), Score, Population Cap,
 * consumption rates, and cost validation.
 */

export class Economy {
    constructor() {
        this.food = 200;
        this.wood = 150;
        this.stone = 80;
        this.bone = 40;
        this.score = 100;

        // Base storage cap per resource (increased by Warehouses)
        this.baseStorage = 500;
        this.storagePerWarehouse = 200;

        // Base population limit
        this.basePopulationCap = 6;
        this.populationPerTent = 4;

        // Food consumption timer
        this.foodDecayTimer = 0;

        // Callbacks for UI updates
        this.onResourceChanged = null;
    }

    /**
     * Checks if tribe has sufficient resources to pay a building cost
     */
    canAfford(cost) {
        if (!cost) return true;
        if (cost.wood && this.wood < cost.wood) return false;
        if (cost.stone && this.stone < cost.stone) return false;
        if (cost.bone && this.bone < cost.bone) return false;
        if (cost.food && this.food < cost.food) return false;
        return true;
    }

    /**
     * Deducts building or upgrade cost
     */
    deductCost(cost) {
        if (!this.canAfford(cost)) return false;
        if (cost.wood) this.wood -= cost.wood;
        if (cost.stone) this.stone -= cost.stone;
        if (cost.bone) this.bone -= cost.bone;
        if (cost.food) this.food -= cost.food;
        this.notifyChange();
        return true;
    }

    /**
     * Deposits harvested resource into tribe stockpile
     * type: 0 = Food, 1 = Wood, 2 = Stone, 3 = Bone
     */
    deposit(resourceType, amount, maxCap = 1000) {
        switch (resourceType) {
            case 0:
                this.food = Math.min(maxCap, this.food + amount);
                break;
            case 1:
                this.wood = Math.min(maxCap, this.wood + amount);
                break;
            case 2:
                this.stone = Math.min(maxCap, this.stone + amount);
                break;
            case 3:
                this.bone = Math.min(maxCap, this.bone + amount);
                break;
        }
        this.addScore(amount * 2);
        this.notifyChange();
    }

    addScore(amount) {
        this.score += amount;
        this.notifyChange();
    }

    /**
     * Calculates current population capacity given active buildings
     */
    getPopulationCap(buildings) {
        const tentsCount = (buildings || []).filter(b => b.type === 2 && b.isConstructed).length;
        return this.basePopulationCap + tentsCount * this.populationPerTent;
    }

    /**
     * Periodic food consumption tick (1 Food per villager every 30 seconds)
     */
    update(villagerCount) {
        this.foodDecayTimer++;
        if (this.foodDecayTimer >= 1800) { // ~30 seconds at 60 fps
            this.foodDecayTimer = 0;
            const consumed = Math.max(1, Math.floor(villagerCount * 0.7));
            this.food = Math.max(0, this.food - consumed);
            this.notifyChange();
        }
    }

    notifyChange() {
        if (this.onResourceChanged) {
            this.onResourceChanged({
                food: this.food,
                wood: this.wood,
                stone: this.stone,
                bone: this.bone,
                score: this.score
            });
        }
    }
}
