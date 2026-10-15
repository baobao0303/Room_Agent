/**
 * Building Module (web/js/game/building.js)
 * Implements 12 authentic prehistoric buildings, construction progression,
 * 3-tier upgrade curves, and footprint rendering.
 */

export const BUILDING_CATALOG = [
    {
        id: 0,
        name: 'Kho vũ khí',
        englishName: 'Armory',
        icon: '⚔️',
        desc: 'Nơi thợ rèn chế tạo vũ khí (chùy gỗ, giáo mác, rìu đá, chùy xương) cho bộ lạc.',
        width: 2,
        height: 2,
        cost: { wood: 15, stone: 5, bone: 0 },
        upgradeCost: { wood: 5, stone: 10, bone: 0 },
        hpTiers: [25, 40, 90],
        capacity: 18,
        prerequisiteId: 2, // Requires Tent
        spriteFrameId: 1714
    },
    {
        id: 1,
        name: 'Phòng tập',
        englishName: 'Barracks',
        icon: '🛡️',
        desc: 'Huấn luyện dân làng thành các Chiến binh dũng cảm với khả năng cận chiến xuất sắc.',
        width: 3,
        height: 2,
        cost: { wood: 20, stone: 10, bone: 0 },
        upgradeCost: { wood: 10, stone: 5, bone: 0 },
        hpTiers: [40, 55, 70],
        capacity: 17,
        prerequisiteId: null,
        spriteFrameId: 1716
    },
    {
        id: 2,
        name: 'Lều',
        englishName: 'Tent / Hut',
        icon: '⛺',
        desc: 'Nơi dân cư trú ngụ và hồi phục thể lực, tăng sức chứa bộ lạc thêm 4 người.',
        width: 5,
        height: 4,
        cost: { wood: 40, stone: 30, bone: 0 },
        upgradeCost: { wood: 15, stone: 15, bone: 0 },
        hpTiers: [70, 100, 90],
        capacity: 4,
        prerequisiteId: null,
        spriteFrameId: 1709
    },
    {
        id: 3,
        name: 'Lều của Tù trưởng',
        englishName: "Chief's Tent",
        icon: '👑',
        desc: 'Tòa nhà chính của Tù trưởng NK2KLove. Trung tâm chỉ huy, không được để bị phá hủy!',
        width: 4,
        height: 4,
        cost: { wood: 30, stone: 20, bone: 0 },
        upgradeCost: { wood: 50, stone: 50, bone: 0 },
        hpTiers: [120, 70, 90],
        capacity: 12,
        prerequisiteId: null,
        spriteFrameId: 1710
    },
    {
        id: 4,
        name: 'Bếp',
        englishName: 'Kitchen',
        icon: '🍲',
        desc: 'Chế biến thịt thú và hoa quả thành thức ăn chín, giảm nạn đói cho toàn bộ tộc.',
        width: 4,
        height: 3,
        cost: { wood: 30, stone: 20, bone: 0 },
        upgradeCost: { wood: 10, stone: 20, bone: 0 },
        hpTiers: [60, 80, 90],
        capacity: 15,
        prerequisiteId: 2, // Requires Tent
        spriteFrameId: 1711
    },
    {
        id: 5,
        name: 'Khu tập ném',
        englishName: 'Range',
        icon: '🏹',
        desc: 'Huấn luyện thợ săn và lính phóng lao tầm xa để đối phó thú dữ từ cự ly an toàn.',
        width: 6,
        height: 4,
        cost: { wood: 40, stone: 30, bone: 0 },
        upgradeCost: { wood: 15, stone: 15, bone: 0 },
        hpTiers: [70, 100, 90],
        capacity: 14,
        prerequisiteId: null,
        spriteFrameId: 1712
    },
    {
        id: 6,
        name: 'Kho',
        englishName: 'Warehouse',
        icon: '📦',
        desc: 'Nơi tập kết tài nguyên do dân làng thu thập về, tăng giới hạn lưu trữ của bộ lạc.',
        width: 3,
        height: 3,
        cost: { wood: 25, stone: 20, bone: 0 },
        upgradeCost: { wood: 18, stone: 18, bone: 0 },
        hpTiers: [50, 70, 90],
        capacity: 16,
        prerequisiteId: null,
        spriteFrameId: 1715
    },
    {
        id: 7,
        name: 'Sân disco',
        englishName: 'Disco Floor',
        icon: '🪩',
        desc: 'Khu vui chơi giải trí thời tiền sử với nước tăng lực Tigerilla, nâng cao tinh thần bộ lạc.',
        width: 5,
        height: 4,
        cost: { wood: 30, stone: 25, bone: 0 },
        upgradeCost: { wood: 10, stone: 25, bone: 0 },
        hpTiers: [90, 110, 90],
        capacity: 13,
        prerequisiteId: 3, // Requires Chief Tent
        spriteFrameId: 1717
    },
    {
        id: 8,
        name: 'Khu thánh địa',
        englishName: 'Sanctuary / Altar',
        icon: '🕯️',
        desc: 'Đàn tế thần linh nơi Pháp sư cầu nguyện hồi máu và bảo vệ làng khỏi dịch bệnh.',
        width: 3,
        height: 3,
        cost: { wood: 0, stone: 20, bone: 10 },
        upgradeCost: { wood: 10, stone: 0, bone: 10 },
        hpTiers: [50, 60, 90],
        capacity: 16,
        prerequisiteId: 1, // Requires Barracks
        spriteFrameId: 1718
    },
    {
        id: 9,
        name: 'Trung tâm pia',
        englishName: 'Scout Center',
        icon: '🧭',
        desc: 'Huấn luyện Trinh sát với tầm nhìn xa và khả năng ngụy trang trong bụi rậm.',
        width: 4,
        height: 4,
        cost: { wood: 30, stone: 15, bone: 0 },
        upgradeCost: { wood: 10, stone: 15, bone: 0 },
        hpTiers: [60, 80, 90],
        capacity: 12,
        prerequisiteId: null,
        spriteFrameId: 1719
    },
    {
        id: 10,
        name: 'Nhà trẻ',
        englishName: 'Nursery',
        icon: '👶',
        desc: 'Trông giữ trẻ em tiền sử an toàn trong khi cha mẹ đi săn bắn và hái lượm.',
        width: 4,
        height: 4,
        cost: { wood: 20, stone: 10, bone: 0 },
        upgradeCost: { wood: 10, stone: 5, bone: 0 },
        hpTiers: [40, 50, 90],
        capacity: 12,
        prerequisiteId: null,
        spriteFrameId: 1720
    },
    {
        id: 11,
        name: 'Chòi canh',
        englishName: 'Watchtower',
        icon: '🗼',
        desc: 'Chòi gác 1x1 nâng cao tầm nhìn và bắn tỉa kẻ địch khi bị tấn công.',
        width: 1,
        height: 1,
        cost: { wood: 10, stone: 10, bone: 0 },
        upgradeCost: { wood: 10, stone: 10, bone: 0 },
        hpTiers: [50, 70, 90],
        capacity: 19,
        prerequisiteId: 1, // Requires Barracks
        spriteFrameId: 1721
    }
];

export class BuildingInstance {
    constructor(def, gridX, gridY, startConstructed = false) {
        this.def = def;
        this.type = def.id;
        this.name = def.name;
        this.x = gridX;
        this.y = gridY;
        this.width = def.width;
        this.height = def.height;

        this.level = 1;
        this.maxHp = def.hpTiers[0] || 100;
        this.hp = startConstructed ? this.maxHp : 10;
        this.isConstructed = startConstructed;
        this.constructionProgress = startConstructed ? 100 : 10; // 0 to 100%

        this.assignedWorkers = [];
        this.sortBias = (def.height * 16) / 2; // for Y-depth sorting
    }

    /**
     * Called by builder villagers when working on this site
     */
    addConstructionWork(amount = 2) {
        if (this.isConstructed && this.hp >= this.maxHp) return;

        this.hp = Math.min(this.maxHp, this.hp + amount);
        this.constructionProgress = Math.floor((this.hp / this.maxHp) * 100);

        if (this.hp >= this.maxHp) {
            this.isConstructed = true;
            this.constructionProgress = 100;
        }
    }

    /**
     * Upgrades building to next tier (Level 2 or 3)
     */
    upgrade() {
        if (this.level >= 3) return false;
        this.level++;
        this.maxHp = this.def.hpTiers[this.level - 1] || (this.maxHp + 30);
        this.hp = this.maxHp;
        return true;
    }

    /**
     * Renders building on world canvas
     */
    render(renderer, isSelected = false) {
        const posX = this.x * 22;
        const posY = this.y * 16;
        const pxW = this.width * 22;
        const pxH = this.height * 16;

        const ctx = renderer.ctx;

        if (!this.isConstructed) {
            // Under construction: render wooden scaffolding & dirt foundation
            ctx.fillStyle = 'rgba(102, 81, 31, 0.7)';
            ctx.fillRect(posX, posY, pxW, pxH);

            // Scaffold diagonal struts
            ctx.strokeStyle = '#a37542';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(posX, posY);
            ctx.lineTo(posX + pxW, posY + pxH);
            ctx.moveTo(posX + pxW, posY);
            ctx.lineTo(posX, posY + pxH);
            ctx.stroke();

            // Construction progress text
            ctx.fillStyle = '#fff';
            ctx.font = '10px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(`${this.constructionProgress}%`, posX + pxW / 2, posY + pxH / 2 + 4);
        } else {
            // Completed: render authentic building sprite frame
            if (this.def.spriteFrameId) {
                renderer.drawFrame(this.def.spriteFrameId, posX, posY - 8);
            } else {
                // Fallback thatched hut style
                ctx.fillStyle = '#6d4c2d';
                ctx.fillRect(posX + 2, posY + 2, pxW - 4, pxH - 4);
            }
        }

        // Draw selection highlight or HP bar if selected or damaged
        if (isSelected) {
            renderer.drawSelectionRing(posX + pxW / 2, posY + pxH / 2, Math.max(pxW, pxH) * 0.4);
        }

        if (this.hp < this.maxHp || isSelected) {
            renderer.drawHealthBar(posX + pxW / 2, posY - 6, this.hp, this.maxHp, Math.min(pxW, 36));
        }
    }
}
