/**
 * Quest Module (web/js/game/quest.js)
 * Manages narrative campaign dialogue, objective evaluation, and quest chapter progression.
 */

export const CAMPAIGN_CHAPTERS = [
    {
        stage: 0,
        title: 'Màn 1: Tan Băng (Thaw)',
        description: 'Kỷ băng hà kết thúc! Tù trưởng NK2KLove cùng bộ lạc rời hang đá. Hãy dựng Lều của Tù trưởng và 1 Kho chứa đồ để bắt đầu xây dựng bộ tộc.',
        objectives: [
            { id: 'build_chief', text: 'Xây dựng Lều của Tù trưởng (Chief Tent)', check: (w) => w.buildings.some(b => b.type === 3 && b.isConstructed) },
            { id: 'build_warehouse', text: 'Xây dựng 1 Kho chứa (Warehouse)', check: (w) => w.buildings.some(b => b.type === 6 && b.isConstructed) },
            { id: 'assign_gatherer', text: 'Phân công ít nhất 1 thợ đốn củi hoặc hái lượm', check: (w) => w.villagers.some(v => v.profession.id === 0 || v.profession.id === 1) }
        ],
        dialogueSequence: [
            { speaker: 'Người dẫn truyện', portrait: 'sprites/pi9_00.png', textIndex: 0 },
            { speaker: 'Người dẫn truyện', portrait: 'sprites/pi9_00.png', textIndex: 1 },
            { speaker: 'Người dẫn truyện', portrait: 'sprites/pi9_00.png', textIndex: 2 },
            { speaker: 'Mumbo', portrait: 'sprites/pi9_01.png', textIndex: 4 },
            { speaker: 'Tù trưởng NK2KLove', portrait: 'sprites/pi9_00.png', textIndex: 5 },
            { speaker: 'Mumbo', portrait: 'sprites/pi9_01.png', textIndex: 6 },
            { speaker: 'Tù trưởng NK2KLove', portrait: 'sprites/pi9_00.png', textIndex: 7 },
            { speaker: 'Mumbo', portrait: 'sprites/pi9_01.png', textIndex: 8 },
            { speaker: 'Tù trưởng NK2KLove', portrait: 'sprites/pi9_00.png', textIndex: 9 },
            { speaker: 'Mumbo', portrait: 'sprites/pi9_01.png', textIndex: 10 },
            { speaker: 'Tù trưởng NK2KLove', portrait: 'sprites/pi9_00.png', textIndex: 11 },
            { speaker: 'Tù trưởng NK2KLove', portrait: 'sprites/pi9_00.png', textIndex: 13 }
        ]
    },
    {
        stage: 1,
        title: 'Màn 2: Nơi Trú Ẩn (Shelter)',
        description: 'Số lượng dân làng đang gia tăng. Hãy dựng thêm 2 Lều cho các gia đình và tích lũy ít nhất 150 Gỗ và 100 Thực phẩm.',
        objectives: [
            { id: 'build_tents', text: 'Xây dựng 2 Lều dân cư (Tent)', check: (w) => w.buildings.filter(b => b.type === 2 && b.isConstructed).length >= 2 },
            { id: 'gather_wood', text: 'Tích lũy tối thiểu 150 Gỗ', check: (w, e) => e.wood >= 150 },
            { id: 'gather_food', text: 'Tích lũy tối thiểu 100 Thực phẩm', check: (w, e) => e.food >= 100 }
        ],
        dialogueSequence: [
            { speaker: 'Tù trưởng NK2KLove', portrait: 'sprites/pi9_00.png', customText: 'Bộ lạc cần nơi trú ngụ vững chắc hơn trước khi thú dữ trong rừng phát hiện ra làng của chúng ta! Hãy mau dựng lều cho dân làng.' },
            { speaker: 'Mumbo', portrait: 'sprites/pi9_01.png', customText: 'Tuân lệnh Tù trưởng! Tôi sẽ điều phối thợ đốn củi đem gỗ về ngay!' }
        ]
    },
    {
        stage: 2,
        title: 'Màn 3: Bếp Lửa & Bếp Ăn (Hearth)',
        description: 'Mọi người cần đồ ăn chín để không bị suy dinh dưỡng. Hãy xây dựng Bếp ăn cho làng.',
        objectives: [
            { id: 'build_kitchen', text: 'Xây dựng 1 Bếp ăn (Kitchen)', check: (w) => w.buildings.some(b => b.type === 4 && b.isConstructed) },
            { id: 'food_surplus', text: 'Dự trữ hơn 200 Thực phẩm', check: (w, e) => e.food >= 200 }
        ],
        dialogueSequence: [
            { speaker: 'Tù trưởng NK2KLove', portrait: 'sprites/pi9_00.png', customText: 'Thịt sống làm dân làng dễ đau bụng! Chúng ta cần một căn Bếp lớn để nấu nướng thức ăn bổ dưỡng.' }
        ]
    }
];

export class QuestEngine {
    constructor(localizationData) {
        this.localization = localizationData;
        this.dialogues = localizationData?.dialogues || [];

        this.currentStage = 0;
        this.currentDialogIndex = 0;
        this.isDialogueActive = false;
        this.completedObjectives = new Set();

        // UI Callbacks
        this.onDialogueShow = null;
        this.onDialogueHide = null;
        this.onQuestCompleted = null;
    }

    /**
     * Starts the intro dialogue sequence for the current campaign chapter
     */
    startIntroDialogue() {
        const chapter = CAMPAIGN_CHAPTERS[this.currentStage];
        if (!chapter || !chapter.dialogueSequence || chapter.dialogueSequence.length === 0) {
            return;
        }

        this.currentDialogIndex = 0;
        this.isDialogueActive = true;
        this.showCurrentDialogueLine();
    }

    showCurrentDialogueLine() {
        const chapter = CAMPAIGN_CHAPTERS[this.currentStage];
        if (!chapter) return;

        const line = chapter.dialogueSequence[this.currentDialogIndex];
        if (!line) {
            this.closeDialogue();
            return;
        }

        let message = line.customText;
        if (!message && line.textIndex !== undefined) {
            message = this.dialogues[line.textIndex] || '...';
        }

        if (this.onDialogueShow) {
            this.onDialogueShow({
                speaker: line.speaker,
                portrait: line.portrait,
                text: message,
                hasNext: this.currentDialogIndex < chapter.dialogueSequence.length - 1,
                hasPrev: this.currentDialogIndex > 0
            });
        }
    }

    nextDialogue() {
        const chapter = CAMPAIGN_CHAPTERS[this.currentStage];
        if (!chapter) return;

        if (this.currentDialogIndex < chapter.dialogueSequence.length - 1) {
            this.currentDialogIndex++;
            this.showCurrentDialogueLine();
        } else {
            this.closeDialogue();
        }
    }

    prevDialogue() {
        if (this.currentDialogIndex > 0) {
            this.currentDialogIndex--;
            this.showCurrentDialogueLine();
        }
    }

    closeDialogue() {
        this.isDialogueActive = false;
        if (this.onDialogueHide) {
            this.onDialogueHide();
        }
    }

    /**
     * Periodic check of quest objectives against current game world and economy
     */
    evaluateObjectives(world, economy, audio) {
        const chapter = CAMPAIGN_CHAPTERS[this.currentStage];
        if (!chapter) return;

        let allComplete = true;

        for (const obj of chapter.objectives) {
            if (!this.completedObjectives.has(obj.id)) {
                if (obj.check(world, economy)) {
                    this.completedObjectives.add(obj.id);
                    if (audio) audio.playFanfare();
                    console.log(`[Quest] Objective completed: ${obj.text}`);
                } else {
                    allComplete = false;
                }
            }
        }

        // Advance to next stage if all objectives satisfied
        if (allComplete && this.currentStage < CAMPAIGN_CHAPTERS.length - 1) {
            this.currentStage++;
            this.completedObjectives.clear();
            if (audio) audio.playFanfare();
            economy.addScore(500);

            if (this.onQuestCompleted) {
                this.onQuestCompleted(CAMPAIGN_CHAPTERS[this.currentStage]);
            }

            // Trigger chapter dialogue
            this.startIntroDialogue();
        }
    }

    getCurrentChapter() {
        return CAMPAIGN_CHAPTERS[this.currentStage] || CAMPAIGN_CHAPTERS[0];
    }
}
