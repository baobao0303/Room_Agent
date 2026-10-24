# QUIZLET PHASE 1: TECHNICAL ARCHITECTURE & DATA MODEL SPECIFICATION

> **Document ID**: `ARCH-QUIZLET-PHASE1-2026-V1`  
> **Parent Epic**: `#681 - [QUIZLET-PHASE1] Quizlet Core Foundation & 3D Flashcards`  
> **Architecture Task**: `#682 - [Lead] Technical Architecture & Data Model for Quizlet Phase 1`  
> **Downstream Tasks**: `#683 (Peer - Data Model, Repo & CSV)`, `#684 (Peer - 3D Flashcards, Hotkeys & TTS)`, `#685 (QC - 5-Stage ISTQB Test Suite)`  
> **Source SRS**: `docs/quizlet_specification.md` (`SPEC-QUIZLET-RE-2026-V1`)  
> **Author**: `Lead (Technical Architect & PM in SLPC)`

---

## 1. ARCHITECTURAL OVERVIEW & SCOPE BOUNDARIES

### 1.1. Scope Decision (Guest / Local Single-Workspace Mode)
Theo Mục 4.1 và Mục 7 của `docs/quizlet_specification.md`:
- **Module 1 (Identity & Access / Auth) KHÔNG TRIỂN KHAI (Out of Scope)**.
- Hệ thống vận hành ở chế độ **Local / Single Workspace / Guest User** mặc định với hằng số `ANONYMOUS_USER_ID = 'guest-local-user'`.
- Lưu trữ dữ liệu cục bộ qua `localStorage` (key: `quizlet_study_sets_v1`) kèm bộ nhớ đệm in-memory (`Map<string, StudySetModel>`) để hoạt động đồng nhất trên trình duyệt, môi trường SSR và Jest JSDOM unit tests với độ trễ đọc/ghi `< 5ms`.

### 1.2. Target Workspace & Folder Structure
Mã nguồn Phase 1 được đặt trong phân hệ `mfe-dashboard` tại `projects/wicx-crm-fe/apps/mfe-dashboard/src/app/quizlet` nhằm tận dụng hạ tầng Angular 18 + Signals + Tailwind CSS + Jest (`apps/mfe-dashboard/jest.config.ts`) mà không gây xung đột với các phân hệ CRM/CDP hiện hữu.

```text
projects/wicx-crm-fe/apps/mfe-dashboard/src/app/quizlet/
├── models/
│   └── study-set.model.ts                       # [Task #683] Domain interfaces, DTOs, constants
├── services/
│   ├── csv-parser.util.ts                       # [Task #683] Pure RFC 4180 CSV/TSV parser & serializer
│   ├── study-set.repository.ts                  # [Task #683] Signals-based CRUD Repository + Diagram Pin + CSV I/O
│   ├── study-set.repository.spec.ts             # [Task #683 / #685] Unit tests for AC-SET-01, AC-SET-02, AC-SET-03
│   └── tts-speech.service.ts                    # [Task #684] Web Speech API TTS Engine + Fallback URL resolver
└── components/
    └── flashcard-player/
        ├── flashcard-player.component.ts        # [Task #684] Angular 18 Signals 3D Flip Card + Global Hotkeys
        ├── flashcard-player.component.html      # [Task #684] GPU-accelerated 3D Flip DOM + ARIA accessibility
        ├── flashcard-player.component.scss      # [Task #684] 3D perspective, preserve-3d, backface-visibility CSS
        └── flashcard-player.component.spec.ts   # [Task #684 / #685] Unit tests for AC-FC-01, AC-FC-02
```

### 1.3. Single-Ownership Invariant (File Isolation Matrix)
Để tuân thủ tuyệt đối nguyên tắc **One Task, One Owner** (không bao giờ để 2 Peer sửa chung 1 file):

| Work Item | Owner | Exclusive Write Scope (Target Files) | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Task #683** | `peer` | `models/study-set.model.ts`<br>`services/csv-parser.util.ts`<br>`services/study-set.repository.ts`<br>`services/study-set.repository.spec.ts` | `AC-SET-01`, `AC-SET-02`, `AC-SET-03` |
| **Task #684** | `peer` | `services/tts-speech.service.ts`<br>`components/flashcard-player/flashcard-player.component.ts`<br>`components/flashcard-player/flashcard-player.component.html`<br>`components/flashcard-player/flashcard-player.component.scss`<br>`components/flashcard-player/flashcard-player.component.spec.ts` | `AC-FC-01`, `AC-FC-02` |
| **Task #685** | `qc` | Thực thi `tools/qc_test_generator.py --sync-harness`, kiểm thử độc lập các file `*.spec.ts` của #683 và #684 | 100% pass `AC-SET-01..02`, `AC-FC-01..02` |

---

## 2. DATA MODEL & STORAGE SCHEMA (TASK #683 SPEC)

### 2.1. Core TypeScript Interfaces (`models/study-set.model.ts`)

```typescript
export const ANONYMOUS_USER_ID = 'guest-local-user';
export const STUDY_SETS_STORAGE_KEY = 'quizlet_study_sets_v1';

export type SupportedLanguageCode = 'en' | 'vi' | 'ja' | 'ko' | 'fr' | 'de' | 'es' | 'zh' | string;

export interface DiagramCoordinates {
  xPercent: number; // 0.0 - 100.0% relative to image width
  yPercent: number; // 0.0 - 100.0% relative to image height
}

export interface TermCardModel {
  id: string;
  setId: string;
  term: string;
  definition: string;
  imageUrl?: string;
  audioUrl?: string;
  isStarred?: boolean;
  displayOrder: number;
  diagramCoordinates?: DiagramCoordinates;
}

export interface StudySetModel {
  id: string; // UUID v4 or deterministic local ID
  creatorId: string; // Defaults to ANONYMOUS_USER_ID
  title: string;
  description: string;
  termLanguage: SupportedLanguageCode; // ISO 639-1 (e.g. 'en', 'vi', 'ja')
  definitionLanguage: SupportedLanguageCode;
  isDiagram: boolean;
  diagramImageUrl?: string;
  cards: TermCardModel[];
  cardCount: number;
  createdAt: string; // ISO-8601 timestamp
  updatedAt: string; // ISO-8601 timestamp
}

export interface CreateTermCardInput {
  id?: string;
  term: string;
  definition: string;
  imageUrl?: string;
  audioUrl?: string;
  isStarred?: boolean;
  displayOrder?: number;
  diagramCoordinates?: DiagramCoordinates;
}

export interface CreateStudySetInput {
  id?: string;
  title: string;
  description?: string;
  termLanguage: SupportedLanguageCode;
  definitionLanguage: SupportedLanguageCode;
  isDiagram?: boolean;
  diagramImageUrl?: string;
  cards: CreateTermCardInput[];
}

export interface CsvParseOptions {
  columnDelimiter?: string; // Default: auto-detect '\t' or ','
  rowDelimiter?: '\n' | '\r\n' | 'auto'; // Default: 'auto'
}

export interface CsvParseResult {
  cards: CreateTermCardInput[];
  skippedRows: number;
  errors: string[];
}
```

### 2.2. Storage & Validation Rules (`services/study-set.repository.ts`)
1. **Validation `AC-SET-01` (Tạo học phần song ngữ)**:
   - `title` sau khi `.trim()` không được rỗng.
   - `termLanguage` và `definitionLanguage` bắt buộc hợp lệ (mặc định `'en'` và `'vi'` nếu không truyền).
   - Danh sách `cards` phải có **tối thiểu 2 thẻ hợp lệ** (`cards.length >= 2`), mỗi thẻ có `term.trim().length > 0` và `definition.trim().length > 0`. Nếu dưới 2 thẻ, ném lỗi `Error('STUDY_SET_MIN_CARDS_REQUIRED: A study set requires at least 2 valid cards')`.
   - Tự động gán `displayOrder` tuần tự (`0, 1, 2, ...`), `isStarred = Boolean(card.isStarred)`, `creatorId = ANONYMOUS_USER_ID`, `cardCount = cards.length`, và lưu đồng bộ vào `localStorage` (`STUDY_SETS_STORAGE_KEY`) + cập nhật Angular Signal `sets`.
2. **Validation `AC-SET-03` (Diagram Sets - Ghim tọa độ sơ đồ)**:
   - Hàm `upsertDiagramPin(setId: string, cardId: string, coords: DiagramCoordinates)` kiểm tra `0 <= coords.xPercent <= 100` và `0 <= coords.yPercent <= 100`. Nếu nằm ngoài biên `[0, 100]`, ném lỗi `Error('INVALID_DIAGRAM_COORDINATES')`.
3. **Signals State API**:
   - `readonly sets: Signal<StudySetModel[]>`
   - `readonly totalSetsCount: Signal<number>`
   - `createSet(input: CreateStudySetInput): StudySetModel`
   - `getSetById(id: string): StudySetModel | undefined`
   - `updateSet(id: string, patch: Partial<CreateStudySetInput>): StudySetModel`
   - `deleteSet(id: string): boolean`
   - `toggleCardStar(setId: string, cardId: string): TermCardModel`
   - `importCardsToSet(setId: string, rawCsv: string, options?: CsvParseOptions): StudySetModel`
   - `createSetFromCsv(meta: Omit<CreateStudySetInput, 'cards'>, rawCsv: string, options?: CsvParseOptions): StudySetModel`
   - `exportSetToCsv(setId: string, delimiter?: ',' | '\t'): string`

### 2.3. RFC 4180 CSV/TSV Import & Export Engine (`services/csv-parser.util.ts`)
Để thỏa mãn `AC-SET-02` (Import thành công file CSV/TSV gồm 50+ thẻ có chứa dấu câu, dấu phân cách và ký tự xuống dòng `\n`, `\r\n`):
- **State-Machine Character Parser (RFC 4180)**:
  - Duyệt từng ký tự với trạng thái `inQuotes: boolean`.
  - Khi `inQuotes === true`:
    - Hai dấu ngoặc kép liên tiếp `""` được unescape thành một dấu `"` trong giá trị trường.
    - Ký tự phân cách cột (`,` hoặc `\t`) và ký tự xuống dòng (`\n`, `\r\n`) bên trong ngoặc kép được **giữ nguyên** là nội dung của `term` hoặc `definition`, không ngắt cột/hàng.
  - Khi `inQuotes === false`:
    - Gặp `columnDelimiter` (`,` hoặc `\t`) -> kết thúc trường hiện tại.
    - Gặp `\r\n` hoặc `\n` -> kết thúc bản ghi thẻ hiện tại.
- **Export RFC 4180 (`exportCardsToCsv`)**:
  - Tự động bọc `"` và nhân đôi `""` nếu `term` hoặc `definition` có chứa delimiter, dấu `"`, hoặc ký tự xuống dòng `\r` / `\n`.

---

## 3. FLASHCARDS 3D FLIP, HOTKEYS & TTS ENGINE (TASK #684 SPEC)

### 3.1. Component Architecture (`components/flashcard-player/flashcard-player.component.ts`)
- **Angular 18 Standards**:
  - `standalone: true`
  - `changeDetection: ChangeDetectionStrategy.OnPush`
  - Quản lý trạng thái 100% bằng **Angular Signals** (`signal`, `computed`) và cú pháp template mới (`@if`, `@for (card of activeCards(); track card.id)`).
- **Signals & State**:
  - `studySet = signal<StudySetModel | null>(null)` (hoặc nhận qua `@Input()` setter cập nhật signal).
  - `currentIndex = signal<number>(0)`
  - `isFlipped = signal<boolean>(false)`
  - `initialSide = signal<'term' | 'definition'>('term')`
  - `isShuffled = signal<boolean>(false)`
  - `filterStarredOnly = signal<boolean>(false)`
  - `lastFlipLatencyMs = signal<number>(0)` (đo thời gian thực thi state flip `< 50ms` phục vụ kiểm chứng `AC-FC-01`).
- **Computed Signals**:
  - `activeCards = computed(() => ...)`: Lọc theo `filterStarredOnly()` và thứ tự `isShuffled()`.
  - `currentCard = computed(() => activeCards()[currentIndex()] ?? null)`
  - `visibleSide = computed<'term' | 'definition'>(() => isFlipped() ? (initialSide() === 'term' ? 'definition' : 'term') : initialSide())`
  - `visibleText = computed(() => ...)`
  - `visibleLanguage = computed(() => visibleSide() === 'term' ? (studySet()?.termLanguage ?? 'en') : (studySet()?.definitionLanguage ?? 'vi'))`
  - `progressText = computed(() => `${currentIndex() + 1} / ${activeCards().length}`)`

### 3.2. 3D Flip Animation & Performance (`AC-FC-01`)
- **CSS GPU Hardware Acceleration (`flashcard-player.component.scss`)**:
  - Scene container: `perspective: 1000px;`
  - Inner 3D stage (`.flashcard-3d-inner`):
    - `transform-style: preserve-3d;`
    - `transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);` (`<= 0.3s`)
    - `transform: translate3d(0, 0, 0) rotateX(0deg);`
    - Khi `.is-flipped`: `transform: translate3d(0, 0, 0) rotateX(180deg);`
  - Front & Back faces (`.flashcard-face`):
    - `backface-visibility: hidden;`
    - `-webkit-backface-visibility: hidden;`
  - Back face (`.flashcard-face-back`):
    - `transform: rotateX(180deg);`
- **Độ trễ phản hồi (`< 50ms`)**:
  - Hàm `toggleFlip()` đảo giá trị `isFlipped.update(v => !v)` đồng bộ trong bộ nhớ cục bộ (không gọi network I/O), cập nhật `lastFlipLatencyMs` đạt `< 50ms`.

### 3.3. Global Keyboard Shortcuts & TTS (`AC-FC-02`)
- **Global Hotkeys (`@HostListener('window:keydown', ['$event'])`)**:
  - Bỏ qua phím tắt nếu `event.target` là `HTMLInputElement`, `HTMLTextAreaElement`, `HTMLSelectElement`, hoặc `isContentEditable === true`.
  - `Space`, `ArrowUp`, `ArrowDown`: Gọi `event.preventDefault()` và `toggleFlip()`.
  - `ArrowRight`: Gọi `nextCard()` (tăng `currentIndex` nếu chưa ở cuối, đồng thời reset `isFlipped.set(false)`).
  - `ArrowLeft`: Gọi `prevCard()` (giảm `currentIndex` nếu `> 0`, đồng thời reset `isFlipped.set(false)`).
  - `KeyS` (hoặc `s` / `S`): Gọi `toggleStarCurrentCard()` để đánh dấu / bỏ đánh dấu sao thẻ hiện tại.
- **Web Speech API TTS Service (`services/tts-speech.service.ts`)**:
  - Chuẩn hóa mã ngôn ngữ ISO 639-1 sang BCP-47 (`'en' -> 'en-US'`, `'vi' -> 'vi-VN'`, `'ja' -> 'ja-JP'`, `'ko' -> 'ko-KR'`).
  - Nếu `typeof window !== 'undefined' && 'speechSynthesis' in window && typeof SpeechSynthesisUtterance !== 'undefined'`:
    - Hủy câu đang đọc (`window.speechSynthesis.cancel()`), khởi tạo `SpeechSynthesisUtterance(text)` với `utterance.lang = resolvedBcp47Lang`, gọi `window.speechSynthesis.speak(utterance)`.
  - Nếu trình duyệt/môi trường không hỗ trợ `speechSynthesis`:
    - Trả về fallback URL `/api/3.0/tts/synthesize?text=${encodeURIComponent(text)}&lang=${encodeURIComponent(lang)}` để phát qua `HTMLAudioElement` hoặc phục vụ kiểm thử.

---

## 4. ACCEPTANCE CRITERIA & VERIFICATION MATRIX (TASK #685)

| Mã AC | Task | Tiêu chí nghiệm thu | Lệnh kiểm thử (Chạy từ `projects/wicx-crm-fe`) |
| :--- | :--- | :--- | :--- |
| `AC-SET-01` | `#683` | Tạo thành công bộ thẻ với tối thiểu 2 thẻ, hỗ trợ song ngữ (`termLanguage`, `definitionLanguage`), lưu vào local storage/DB ở chế độ Guest/Local (`guest-local-user`). Chặn tạo bộ thẻ có `< 2` thẻ. | `npx jest --config apps/mfe-dashboard/jest.config.ts apps/mfe-dashboard/src/app/quizlet/services/study-set.repository.spec.ts` |
| `AC-SET-02` | `#683` | Import thành công file CSV/TSV gồm 50 thẻ có chứa dấu câu, dấu phẩy/tab trong ngoặc kép và ký tự xuống dòng (`\n`, `\r\n`) theo chuẩn RFC 4180. | `npx jest --config apps/mfe-dashboard/jest.config.ts apps/mfe-dashboard/src/app/quizlet/services/study-set.repository.spec.ts` |
| `AC-SET-03` | `#683` | Cắm ghim tọa độ `(xPercent, yPercent)` trong khoảng `[0, 100]` trên học phần sơ đồ (`isDiagram: true`). | `npx jest --config apps/mfe-dashboard/jest.config.ts apps/mfe-dashboard/src/app/quizlet/services/study-set.repository.spec.ts` |
| `AC-FC-01` | `#684` | Lật thẻ 3D mượt mà (`perspective: 1000px`, `preserve-3d`, `backface-visibility: hidden`) qua click chuột, chạm hoặc phím `Space` với độ trễ `< 50ms`. | `npx jest --config apps/mfe-dashboard/jest.config.ts apps/mfe-dashboard/src/app/quizlet/components/flashcard-player/flashcard-player.component.spec.ts` |
| `AC-FC-02` | `#684` | Điều hướng thẻ qua phím mũi tên (`ArrowLeft`, `ArrowRight`, `ArrowUp`, `ArrowDown`), đánh dấu sao bằng `KeyS`, và phát âm TTS chuẩn xác theo ngôn ngữ của mặt thẻ đang hiển thị (`termLanguage` / `definitionLanguage`). | `npx jest --config apps/mfe-dashboard/jest.config.ts apps/mfe-dashboard/src/app/quizlet/components/flashcard-player/flashcard-player.component.spec.ts` |
