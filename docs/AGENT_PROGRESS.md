# Sổ Cái Tiến Độ & Bàn Giao Giữa Các Agent (Agent Progress & Handoff Ledger)

> **QUY TẮC BẮT BUỘC CHO MỌI AGENT**:
> 1. Khi User yêu cầu **"làm tiếp"**, **"tiếp tục"**, hoặc **"báo cáo những gì đã làm"**, Agent phải đọc file này đầu tiên (hoặc chạy `python3 tools/agent_progress.py status`) để báo cáo ngay cho User trước khi bắt tay vào việc.
> 2. Sau khi hoàn thành một đầu việc hoặc trước khi dừng chờ User, Agent phải cập nhật lại tiến độ bằng lệnh `python3 tools/agent_progress.py log ...`.

---

## 1. Trạng thái Tổng quan Hiện tại (Current Snapshot)

- **Cập nhật lần cuối**: `2026-10-19 00:08:30 +0700`
- **Agent cập nhật gần nhất**: `Supervisor`
- **Trọng tâm hiện tại**: Khôi phục bảng Kanban SLPC Harness — Floci DynamoDB cho Admin
- **Hành động kế tiếp (Khi User bảo "làm tiếp")**:
  > Chờ User kiểm tra lại bảng Kanban trên giao diện Aevum và nghiệm thu giao diện DetailCustomerComponent

---

## 2. Những Hạng Mục Đã Hoàn Thành (Completed Items)

- [x] Đọc và phân tích toàn bộ mã nguồn workspace `/home/baoltb/Desktop/Paseo_Project` (AGENTS.md, CLAUDE.md, setup_home.sh, setup_harness.sh, patch_paseo.py, profiles/*, scripts/*, tools/*, docs/spec/*, game/*).
- [x] Clone repo `https://github.com/hoangnb24/codex-room-setup` vào `/home/baoltb/Desktop/Paseo_Project/codex-room-setup` và thêm `/codex-room-setup/` vào `.gitignore`.
- [x] Đọc 100% mã nguồn của `codex-room-setup` (`install`, `scripts/install-room`, `scripts/install-paseo`, `scripts/verify`, `scripts/doctor`, `home/.local/bin/codex-room*`, `home/.config/codex-room/*`, `home/.paseo/config.json.template`).
- [x] Chạy kiểm chứng mã nguồn `./scripts/verify --source` (đạt 100% `VERIFY_OK`) và chẩn đoán máy trạm qua `./scripts/doctor` & `./install --dry-run`.
- [x] Tạo và hoàn thiện tài liệu đặc tả 8 mục tại `docs/spec/codex-room-setup-spec.md`.
- [x] Xây dựng hệ thống Sổ cái Tiến độ & Bàn giao Agent (`docs/AGENT_PROGRESS.md` + `tools/agent_progress.py`) và tích hợp vào `AGENTS.md`, `CLAUDE.md`.
- [x] Checkout nhánh feat/rea-prehistoric-tribes-remake|Khởi chạy HTTP server cho game tại http://127.0.0.1:8080/ (thư mục games/bolacthoitiensu/web)|Mở trình duyệt để chơi game
- [x] Đọc 100% mã nguồn Web Remake (web/index.html, web/css/style.css, web/js/main.js, web/js/engine/*, web/js/game/*)|Đọc mã nguồn Decompiled J2ME (decompiled/tribes.java, a.java..f.java), RECONSTRUCTION_SPEC.md, scripts/extract_all.py và verify_all.py|Tạo tài liệu đặc tả chi tiết 10 mục tại docs/spec/bolacthoitiensu-remake-spec.md
- [x] Đọc /Users/bao312/Desktop/Room_Agent/spec.md|Tạo tài liệu Complete Build Prompt cho Bộ Lạc Thời Tiền Sử tại docs/spec/bolacthoitiensu-build-prompt.md theo đúng cấu trúc của spec.md|Hoàn thiện bản thảo prompt_draft.md (Step 9 - Ready for launch) cho teamwork_preview
- [x] Chạy 100% xanh typecheck, vitest (44 tests), build Vite, CDP smoke test (819,200 non-blank pixels), 260 E2E tests, xác thực git status bolacthoitiensu sạch sẽ
- [x] Initialized Vite+TS+Three.js project
- [x] implemented Renderer with soft shadows
- [x] CameraController with non-inverted strafe basis
- [x] 5-zone mathematical Terrain
- [x] custom GLSL Water and Sky shaders
- [x] FoliageInstancer with dither proximity dissolve
- [x] 5-bus procedural Web Audio
- [x] Presets
- [x] 21/21 vitest tests passing
- [x] npm run build passing with 0 errors
- [x] games/bolacthoitiensu untouched
- [x] Xác thực 100% bảo toàn games/bolacthoitiensu (0 file sửa đổi/xóa)|Xác thực build sạch npm run build (tsc && vite build)|Chạy 21/21 vitest unit & smoke tests đạt 100% pass|Kiểm thử độc lập 10.000 điểm địa hình, ma trận camera strafe 360 độ, 5 bus Web Audio|Phân tích mã nguồn không có mock/facade/hardcoded output
- [x] 1. Fixed dry valley floor baseline (2.55m-3.2m) in src/world/Terrain.ts so only stream, marsh (25,45), and crater (60,-10) dip below waterLevel 1.5m
- [x] 2. Added shoreline wave damping (shoreDamp) and dry-ground fragment discard in src/world/WaterShader.ts
- [x] 3. Fixed post-lerp camera elevation clamping in CameraController.ts and grass/dither in FoliageInstancer.ts
- [x] 4. Verified 69/69 Vitest tests and Vite build pass.
- [x] Empirically verified raycast ghost placement, footprint collision overlap, scaffolding progression, and 3-tier visual upgrade mesh swapping across all 12 buildings. Added 21 tests in test/m2_adversarial_stress.test.ts. All 155 tests pass (0 failures), npm run build passes.
- [x] Verified CRITICAL RULES 2, 3, 5, 8-state FSM, combat, preservation invariant, authored m3_adversarial_stress.test.ts (13 tests), full test suite 235/235 passing, production build passing
- [x] 1. Verified water & river channel look clean in user screenshot
- [x] 2. Sent urgent directive to m4_worker_1 (93a906e7-de57-4057-bf7b-37b5d348d9c2) and Sentinel (fe0d47e2-63d7-4910-baf7-b4372ccae099) to immediately mount GlassmorphicHUD.ts (12 building buttons, 3D ghost preview raycast click-to-place, upgrades, weapon crafting, traps, and resource bar) into src/main.ts.
- [x] 1. Fixed Object.values(BUILDING_CATALOG/WEAPON_CATALOG/TRAP_CATALOG) in GlassmorphicHUD.ts so 3D render loop and 12 building buttons render cleanly
- [x] 2. Moved initial resource nodes and beasts to dry land (>= 1.85m) in src/main.ts and added dry-land roaming guards (>= 1.55m) in BeastEntity.ts and VillagerAI.ts
- [x] 3. Verified tsc && vite build passes with 0 errors.
- [x] 1. Implemented CampaignManager.ts (4-chapter narrative campaign, boss spawns, causeway repair, victory conditions).|2. Implemented TutorialSystem.ts (5-step auto-clearing tutorial with skip/reset).|3. Implemented ObjectiveIndicator.ts (3D gold floating arrow + screen-edge frustum clamping).|4. Implemented GlassmorphicHUD.ts (complete HTML/CSS overlay, 12 buildings, 6 weapons, 3 traps, Shaman heal, inspector, save/load, quality).|5. Implemented SaveLoadSystem.ts (in-place live 3D scene mutation rehydration).|6. Wired procedural audio triggers into AudioManager.ts.|7. Created comprehensive test suite test/campaign_tutorial_saveload.test.ts (17 tests).|8. Verified 258/258 Vitest tests (13 test files) pass with 0 errors.|9. Verified npm run build passes with 0 errors.|10. Verified games/bolacthoitiensu untouched.
- [x] 1. Wired #btn-order-gather, #btn-order-rest, #btn-order-train click handlers in GlassmorphicHUD.ts
- [x] 2. Added orderVillagerGather() and right-click raycast tree/resource/construction command dispatch in src/main.ts
- [x] 3. Added Vietnamese AI state indicator (Đang khai thác 🪓, Đang xây dựng 🔨, Đang cất kho 📦) on the villager inspector card
- [x] 4. Verified 258/258 tests and Vite build pass.
- [x] Xuất bản TEST_READY.md tại TEST_READY.md và .agents/teamwork/TEST_READY.md
- [x] Tạo bộ test E2E hoàn chỉnh test/e2e_complete_suite.test.ts (8 bài test Tier 4 và WebGL headless scene instantiation)
- [x] Chạy 19/19 test files đạt 359/359 pass (0 failures)
- [x] Build production npm run build đạt 100% green
- [x] Kiểm chứng games/bolacthoitiensu giữ nguyên 100% không suy suyển
- [x] Lập báo cáo bàn giao handoff.md tại .agents/teamwork/m5_worker_1/handoff.md
- [x] All 5 milestones complete, 392/392 tests pass, clean build, victory audit confirmed
- [x] 1. All 5 Milestones passed with 392/392 tests across 21 test suites
- [x] 2. Clean production Vite + TypeScript build (0 errors)
- [x] 3. Preserved legacy bolacthoitiensu 100% untouched
- [x] 4. Verified interactive HUD controls (#btn-order-gather, #btn-order-rest, #btn-order-train, #btn-focus-objective, bottom Construction Deck) and 3D WebGL scene (>70k–323k triangles, 0 shader errors).
- [x] 8/8 unit tests pass 100%, chạy demo main.rs ghi nhận và đọc dữ liệu offline hoàn hảo
- [x] Embedded Notion-like web editor UI, Created REST API for block CRUD and offline action queuing, Integrated auto-open browser on macOS
- [x] Khởi chạy daemon background tiến trình Notion Offline Rust lắng nghe port 3000,Kiểm thử curl /api/blocks phản hồi thành công
- [x] Build release Rust binary và restart daemon port 3000
- [x] Triển khai đầy đủ execSqliteBatchV2, execSqliteBatchInternal, ErrorBefore cascade, onError handler, attemptToBackupAndResetDatabase (giới hạn 3 lần), publishHealthSnapshot
- [x] 13/13 unit tests pass 100% trong Rust
- [x] Khởi chạy daemon Notion Offline Rust phục vụ endpoint /api/sqlite/health, /api/sqlite/batch_v2, /api/sqlite/recover trên port 3000
- [x] 16/16 unit tests pass 100%, server release chạy ổn định tại http://127.0.0.1:3000, đầy đủ slash menu, gutter, cover, icon picker, markdown triggers và SQLite WAL defensive mode
- [x] 16/16 Rust unit tests pass 100%, build release và restart daemon port 3000
- [x] Tạo FT-01, FT-02, FT-03
- [x] Tạo TK-01, TK-02, TK-03 trên Harness DB
- [x] Spawn 3 Peer sub-agents qua Paseo runner (c9a80db7, 806588c4, e1a86dd3)
- [x] Triển khai bảng updates và blobs, API endpoints đồng bộ cho Task #5
- [x] Mở rộng BlockType enum trong models.rs, render DOM/HTML trong server.rs, 24/24 tests passed
- [x] Tất cả 24 unit tests pass
- [x] Release binary compiled
- [x] Endpoint updates, blobs, batch_v2, health hoạt động ổn định trên port 3000
- [x] Caret cross-block navigation & markdown triggers hoạt động chuẩn xác
- [x] Chạy 5-stage ISTQB qc_test_generator cho Task #5 tạo 20 testcases
- [x] Chạy cargo test 24/24 passed
- [x] Đóng 20 testcases và Task #5 trên Harness DB chuyển Lead
- [x] Chạy 5-Stage ISTQB test generator cho Task #6 (REQ 100%, CI 100%, Symbols 100%)
- [x] Chạy 24/24 unit tests pass (/Users/bao312/.cargo/bin/cargo test)
- [x] Đóng 40 child testcases và đóng Task #6 sang Closed chuyển Lead
- [x] Chạy 5-Stage ISTQB pipeline cho Task #7 (18 testcases, REQ=100%, CI=100%, Symbols=100%)
- [x] Verify thành công 25/25 Rust unit tests trong server.rs
- [x] Đóng toàn bộ 18 child testcases trên Harness DB
- [x] Đóng Task #7 chuyển Lead nghiệm thu Feature #4 và Epic #1
- [x] Khởi tạo Epic #86 (EP-02)
- [x] Khởi tạo Feature #87 (FT-04 - Multi-property Schema)
- [x] Khởi tạo Feature #88 (FT-05 - Table & Kanban UI)
- [x] Khởi tạo Feature #89 (FT-06 - Filter/Sort/Search)
- [x] Khởi tạo Task #90 (TK-04 - Database block schema & CRUD API)
- [x] Dispatch agent Lead qua Paseo (id: 06ff78eb-e8e0-4280-b778-cd6544e8d61d)
- [x] Thiết kế kiến trúc AFFiNE Database Data-View Engine (docs/spec/affine-database-dataview-engine-spec.md)
- [x] Tạo Task #91 (TK-05 REST endpoints)
- [x] Tạo Task #92 (TK-06 Table View UI)
- [x] Tạo Task #93 (TK-07 Kanban Board UI)
- [x] Tạo Task #94 (TK-08 Filter & Search engine)
- [x] Tạo Task #95 (TK-09 Multi-column Sort engine)
- [x] Dispatch Peer thực thi Task #90
- [x] Triển khai Database/DatabaseRow BlockType và markdown AST
- [x] Triển khai domain structs ColumnSchema, DataViewConfig, CellValue, DatabaseProperties, DatabaseDetail
- [x] Triển khai 6 persistence helper methods trên NotionDb (create, get, add_column, insert_row, update_cell, get_rows)
- [x] Bổ sung 6 unit test mới, 31/31 unit test PASS (100%)
- [x] Chạy toàn bộ 31 unit test trong crate notion-offline-rust (31/31 PASS)
- [x] Xác nhận AC-1 đến AC-4 của Task #90 (TK-04) đáp ứng 100%
- [x] Chuyển trạng thái Task #90 thành Closed trên Harness DB
- [x] Tự động dọn dẹp biên bản phòng bàn giao bmad/rooms/
- [x] Đóng Task #91 và Feature #87 trên Harness DB
- [x] Nghiệm thu & đóng Task #92 (Table View Component với Inline Editing)
- [x] Nghiệm thu & đóng Task #93 (Kanban Board Component với Drag-and-Drop)
- [x] Nghiệm thu & đóng Feature #88 (FT-05 - Data-View Table & Kanban Board UI)
- [x] Kiểm thử toàn diện 33/33 unit tests pass 100%
- [x] Fix assertion test_database_view_presets_crud trong src/db.rs
- [x] Toàn bộ 38/38 unit tests pass 100%
- [x] Đóng Task #94, Task #95, Feature #89 và Epic #86 trên Harness DB
- [x] Động cơ lọc điều kiện & tìm kiếm (Filter & Search) và sắp xếp đa cột (Multi-column sort) trên Rust SQLite đạt 38/38 unit tests pass 100%, đóng Task #94, Task #95, Feature #89 và Epic #86 trên Harness DB
- [x] Hoàn thành EP-03 Edgeless Whiteboard Canvas Engine (Epic #256)
- [x] Kích hoạt Peer qua Paseo (ID: 45366d8e), chuyển Task #265 sang Active trên Harness DB
- [x] Triển khai domain structs PageNode, BreadcrumbItem, MovePageReq trong models.rs
- [x] Triển khai get_workspace_page_tree, get_page_breadcrumbs, move_page trong db.rs
- [x] Triển khai REST endpoints GET /api/pages/tree, GET /api/pages/:id/breadcrumbs, POST /api/pages/:id/move và POST /api/pages/move trong server.rs
- [x] Bổ sung bộ test integration test_workspace_hierarchy_rest_endpoints và sửa lỗi format response
- [x] Đạt 49/49 unit & integration tests pass 100%
- [x] Chạy 5-Stage ISTQB test generator cho src/db.rs đạt 100% REQ/CI/Symbols coverage
- [x] Tạo và đóng 10 child Testcases (#268-#277)
- [x] Chạy toàn bộ test suite notion-offline-rust đạt 51/51 PASS
- [x] Chuyển trạng thái Task #265 sang Closed trên Harness DB bàn giao cho Lead
- [x] Tạo Feature FT-11 (#278)
- [x] Tạo Task TK-16 (#279)
- [x] Dispatch Peer agent db877323
- [x] Xuất bản tài liệu đặc tả docs/spec/affine-complete-architecture-spec.md
- [x] Bổ sung biến môi trường FLOCI_ENDPOINT, FLOCI_S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION vào mục 6.2 của docs/spec/affine-complete-architecture-spec.md
- [x] Cập nhật bảng ma trận tính năng và biến môi trường toàn hệ thống AFFiNE
- [x] Thêm các biến môi trường REDIS_SERVER_HOST/PORT/PASSWORD và DATABASE_URL vào spec kiến trúc AFFiNE phục vụ triển khai backend tương lai
- [x] Tao Epic #280 tren Harness DB va spawn agent Lead de thiet ke kien truc va phan ra task
- [x] Phan ra kien truc Epic #280 thanh 4 Features (FT-12: Scaffold & SQLite WAL, FT-13: y-octo CRDT, FT-14: BlockSuite Data-View, FT-15: Floci S3 Sync)
- [x] Tao 4 Feature #281, #282, #283, #284 tren ban co Harness
- [x] Tao Task #285 va dispatch cho Peer qua Paseo
- [x] Tao Task #286, #287, #288 tren Harness backlog
- [x] Scaffolded Cargo workspace affine-standalone
- [x] Implemented affine-storage schema v2 DDL
- [x] Implemented SQLite WAL pool and foreign keys false
- [x] Implemented checkpoint and hot vacuum_into backup
- [x] Implemented CRUD for meta, snapshots, updates, clocks, blobs, peer_clocks
- [x] Added 8 comprehensive integration tests in storage_test.rs
- [x] All tests passing
- [x] Chay cargo test affine-standalone/crates/storage pass 8/8 tests
- [x] Kiem tra 4/4 Acceptance Criteria dat 100%
- [x] Chuyen trang thai Task #285 sang Closed tren Harness DB
- [x] 1. Nghiem thu va Dong Feature #281 (FT-12: Scaffold & SQLite WAL)|2. Chuyen Feature #282 sang Active tren Harness Floci DynamoDB|3. Chuyen Task #286 sang Active va dispatch cho Peer qua Paseo (agent 2aea6e60)
- [x] Tạo crate affine-crdt với error, compression, snapshot, engine, compaction modules
- [x] Viết 15 unit/integration tests kiểm thử CRDT merge, zstd compression, bincode serialization và SQLite prune
- [x] Pass 100% tests workspace
- [x] Chay thanh cong toan bo 15/15 unit & integration tests cua affine-crdt
- [x] Dat 100% REQ/CI/Symbol coverage theo 5-Stage ISTQB gate
- [x] Sync 8 testcases len Harness DB
- [x] Chuyen trang thai Task #286 thanh Closed
- [x] 1. Phân tích clone/AFFiNE bằng REA v6.5.0 thu được 4 Evidence IDs (electron, blocksuite/model, web, server)|2. Xây dựng 5 crates trong affine-standalone: affine-storage (SQLite WAL v2), affine-crdt (y-octo + zstd + bincode), affine-model (BlockSuite 7-column Data-View, Filter/Sort, Edgeless Surface, Page Tree), affine-sync (Floci S3 + SharedPreferencesStore), affine-server (HTTP API + Full SPA UI)|3. Pass 100% cargo test (7/7 test suites)|4. Khởi chạy live server tại http://127.0.0.1:3000
- [x] Tao avatar SVG va PNG cho Aevum
- [x] Tao Task #313 tren Harness DB
- [x] Dispatch Peer agent 8ecd31d0-0f29-4e69-8cf3-6d9302b713cc
- [x] Đã dừng tiến trình dev server 8081 an toàn, di chuyển toàn bộ thư mục từ clone/AFFiNE sang projects/AFFiNE, xóa thư mục rỗng clone/
- [x] Đổi tên thư mục projects/AFFiNE thành projects/aevum
- [x] cập nhật DocumentTitle, AevumIcon, AevumLogo, AuthHeader, Onboarding Logo, server-name, cloud constant, backend config resolver và 149 bản dịch i18n
- [x] Đã liên kết nhị phân agy từ ~/.gemini/bin/agy vào ~/.local/bin, ~/.gemini/antigravity-ide/bin, /usr/local/bin và chạy agy install cấu hình hoàn chỉnh PATH
- [x] Cấu hình CLI hỗ trợ alias @aevum/web, aevum, web
- [x] bổ sung scripts dev:aevum, dev:web, aevum
- [x] cập nhật yarn dev tự động trỏ đến @aevum/web
- [x] Đã gỡ bỏ AppDownloadButton khỏi root-app-sidebar/index.tsx
- [x] Đã bật hot: true và cấu hình webSocketURL tự động nhận diện port 8081 thay vì cố định port 8080 trong tools/cli/src/bundle-shared.ts
- [x] Cập nhật patch_paseo.py và tools/paseo_hooks.py hỗ trợ đường dẫn Paseo.app trên macOS, nạp đủ 10 profiles (Supervisor, Lead, Peer, QC, Lead BA, Peer BA, Lead design, Peer Design, Lead Dev, Peer Dev) và kích hoạt paseo reload + slpc-lifecycle-hooks plugin
- [x] Compiled affine_server_native Rust module with macOS SDK, migrated runtime tables on backend startup, added instant OTP dispatch logging to backend console, verified account registration and frontend proxy /api
- [x] Removed hardcoded minHeight from SignInDialog and authContainer to fix bottom redundant space
- [x] retrieved OTP 388827 for lcho332002@gmail.com
- [x] explained password vs magic link architecture
- [x] Updated authFooter in share.css.ts with marginTop: 24px, enabled style/className passing in AuthFooter and Back components for clean separation
- [x] Cập nhật profiles/supervisor.md, profiles/lead.md, profiles/peer.md, profiles/qc.md, patch_paseo.py, tools/call_agent.py sang provider=antigravity, model=gemini-4-argon-high, modeId=full-access và reload Paseo Daemon
- [x] 1. Frontend (sign-in.tsx): Thêm ô nhập Password (AuthInput type=password, id=current-password, autoComplete=current-password) ngay dưới ô Email trong SignInStep
- [x] đổi hàm submit onContinue từ checkUserByEmail (/api/auth/preflight) sang gọi trực tiếp authService.signInPassword ({ email, password }) tới POST /api/auth/sign-in. 2. Backend (service.ts, user.ts, controller.ts): Cập nhật AuthService.passwordLogin tự động khởi tạo tài khoản mới (nếu allowSignup bật) hoặc gán mật khẩu cho tài khoản chưa có password trước khi xác thực Argon2 qua runtime password_login
- [x] cập nhật /api/auth/preflight trả về password.available = true.
- [x] 1. Đổi DEFAULT_WORKSPACE_NAME từ 'Demo Workspace' sang 'Aevum Workspace' trong constant.ts
- [x] 2. Tắt createFirstAppData và loại bỏ giải nén onboarding.zip trong first-app-data.ts
- [x] 3. Thêm hiệu ứng backdrop-filter: blur(18px) cho Modal overlay & SignInDialog, khóa đóng modal khi chưa đăng nhập
- [x] 4. Chặn hiển thị WorkspacePage khi chưa đăng nhập (hiển thị AppContainer fallback mờ), tự động xóa các local demo workspace cũ trong IndexedDB và chỉ mở/tạo cloud workspace sau khi authenticated.
- [x] 1. Căn giữa hoàn toàn tiêu đề AuthHeader (Sign in to Aevum / Aevum Self-hosted) trong auth-header.tsx và share.css.ts
- [x] 2. Thêm MainFallbackContent (gồm SignInBackgroundArts, ambient radial glow và workspace/document skeleton không chứa Demo) vào AppContainer và giảm độ tối/blur (5px + 8px backdrop) để thấy rõ nền mờ phía sau modal
- [x] 3. Thêm noValidate cho form, chuẩn hóa validate Email & Password đồng thời (bắt buộc nhập, đúng định dạng email, validate sau tương tác onBlur/onChange, tự động focus ô lỗi đầu tiên, kèm icon cảnh báo và viền đỏ focus ring trong AuthInput).
- [x] 1. Gọi POST http://localhost:3010/api/auth/sign-in để khởi tạo tài khoản admin@aevum.io (mật khẩu Admin@123456)
- [x] 2. Cập nhật PostgreSQL DB (bảng users và user_features) cấp quyền administrator, free_plan_v1 và unlimited_copilot cho admin@aevum.io và baoltb@aevum.app.
- [x] 1. Loại bỏ MainFallbackContent (hộp banner tím, 6 ô vuông xám và SignInBackgroundArts hình đám mây/ổ khóa/màn hình) cùng thanh skeleton nhấp nháy
- [x] 2. Thay bằng UnauthenticatedWorkspaceBackdrop hiển thị giao diện Aevum Workspace thật, tối giản, đồng bộ (Sidebar trái với Aevum Workspace, Search, All docs, Journals, Settings + khung trang sạch sẽ không có Demo Workspace hay tài liệu demo) được làm mờ nhẹ (blur 4px + backdrop-filter 8px).
- [x] 1. Thay thế color: cssVar('blue') bằng color: 'currentColor' trên suffixStyle của ArrowRightBigIcon trong sign-in.tsx
- [x] 2. Dọn dẹp import cssVar không còn sử dụng trong sign-in.tsx.
- [x] 1. Đổi @affine/monorepo -> @aevum/monorepo và @affine-tools/cli -> @aevum-tools/cli trong package.json gốc, tools/cli/package.json và các workspace liên quan. 2. Cập nhật AuthHeader (auth-header.tsx, share.css.ts, sign-in.tsx, sign-in-with-password.tsx): bỏ dòng phụ đề Aevum Self-hosted, tăng kích thước AevumIcon lên 56px đặt ở trên cùng căn giữa, và đưa dòng tiêu đề Sign in to Aevum xuống dưới căn giữa.
- [x] 1. Tạo file video H.264 1280x720 30fps lặp mượt (packages/frontend/core/public/aevum-auth-bg.mp4) bằng AVAssetWriter & CoreGraphics
- [x] 2. Tích hợp thẻ <video autoPlay loop muted playsInline src='/aevum-auth-bg.mp4' /> kèm hiệu ứng blur(24px) làm hình nền mờ trong UnauthenticatedWorkspaceBackdrop (app-container/index.tsx).
- [x] Chỉ render authInputError khi có lỗi (thay vì luôn giữ 20px+ khoảng trống bằng visibility: hidden), chỉnh marginBottom của authInputWrapper về 12px (10px khi có lỗi), thu gọn khoảng cách label xuống 4px và thêm marginTop 4px cho nút Sign-In
- [x] Tăng marginBottom của authInputWrapper từ 12px lên 18px (14px khi có hint), tăng khoảng cách label-input từ 4px lên 6px, và tăng marginTop của nút Sign in từ 4px lên 8px
- [x] 1. auth-header.tsx & share.css.ts: Điều chỉnh AevumIcon về 46px, tiêu đề Sign in to Aevum về 18px (font-weight: 600, letter-spacing: -0.01em), nhãn Email/Password về 13px (font-weight: 500), nội dung ô nhập về 14px (font-weight: 400). 2. input/style.css.ts & button.css.ts: Sửa lỗi thiếu đơn vị px ở fontSizeVar ('15' -> '14px', font-weight: 500) trên button extraLarge và cho thẻ <input> kế thừa font-size 14px đồng bộ.
- [x] 1. Xóa script affine/af và file affine.ts cũ ở root package.json, chỉ giữ aevum/ae. 2. Đổi toàn bộ cấu hình docker-compose.backend.yml, render.yaml, typedoc.json, .gitignore, LICENSE, SECURITY.md, CHANGELOG.md từ affine/AFFiNE sang aevum/Aevum. 3. Cập nhật metadata & scripts (aevum bundle) trong 12 file package.json của các workspace packages và tools/cli, tools/utils. 4. Cập nhật toàn bộ 25 file ngôn ngữ i18n (packages/frontend/i18n/src/resources/*.json) và hơn 100 file giao diện/backend hiển thị tên dự án từ AFFiNE sang Aevum.
- [x] 1. Dùng git rm --cached gỡ bỏ toàn bộ các thư mục ngoài packages/backend và packages/frontend (như blocksuite, tools, tests, docs, scripts, packages/common, .cargo, .github, .docker...) khỏi Git mà vẫn giữ nguyên file trên ổ đĩa local để dev server chạy bình thường. 2. Cập nhật .gitignore để chỉ theo dõi packages/backend, packages/frontend và các file cấu hình gốc cần thiết. 3. Commit và push lên origin/main.
- [x] 1. Tạo lại file video packages/frontend/core/public/aevum-auth-bg.mp4 với nền đen tuyền và hiệu ứng chuyển động xám than tối giản. 2. Cập nhật UnauthenticatedWorkspaceBackdrop trong packages/frontend/core/src/desktop/components/app-container/index.tsx sang nền đen #000000. 3. Đổi DEFAULT_SELF_HOSTED_SERVER_NAME từ Aevum Self-hosted thành Aevum. 4. Commit và push lên origin/main.
- [x] 1. Cập nhật desktop/pages/index/index.tsx và desktop/pages/workspace/index.tsx để điều hướng thẳng vào trang Select (WorkspaceNavigator) thay vì ép bật ngay Sign-In modal
- [x] 2. Bật nút Add a self-hosted server (AddServer) trên Web trong WorkspaceNavigator và trong SignInStep
- [x] 3. Render lại video aevum-auth-bg.mp4 chuẩn giao diện Aevum Dark Workspace (Sidebar, Table/Kanban, Edgeless Mind-Map, AI Copilot) với độ mờ blur(5px).
- [x] Thêm revalidate danh sách workspace và tự động tạo/mở Aevum Workspace sau khi người dùng đăng nhập từ màn hình Select
- [x] 1. Render ảnh /Users/bao312/Downloads/florindumitrache-sky-4949913_1920.jpg thành video 1920x1080 30fps loop mượt 10 giây (packages/frontend/core/public/aevum-auth-bg.mp4) với hiệu ứng Ken Burns, sao lấp lánh, vệt sao băng chuyển động và ánh lửa trại bập bùng. 2. Thêm ảnh poster packages/frontend/core/public/aevum-auth-bg.jpg và cập nhật UnauthenticatedWorkspaceBackdrop trong packages/frontend/core/src/desktop/components/app-container/index.tsx để hiển thị sắc nét không bị mờ. 3. Commit và push lên origin/main.
- [x] Truyền trực tiếp prop close vào onSkip={close} của SignInPanel trong desktop/dialogs/sign-in/index.tsx
- [x] 1. Xóa (inpaint) vệt sao băng trắng tĩnh trong ảnh gốc tại phương trình y = 546 + 0.26545 * (x - 595) để bầu trời sạch khi sao băng chưa bay qua. 2. Quy đổi chính xác hệ tọa độ ảnh 1920x1282 sang khung hình video 1920x1080 và vẽ sao băng có đầu sáng + đuôi vuốt mảnh bay khớp 100% quỹ đạo. 3. Cập nhật cache-buster /aevum-auth-bg.mp4?v=6, commit và push lên origin/main.
- [x] 1. Thêm preload=auto và <link rel=preload> cho /aevum-auth-bg.mp4?v=7 và /aevum-auth-bg.jpg?v=7 trong template.html. 2. Mount UnauthenticatedWorkspaceBackdrop ngay từ đầu và chờ sự kiện onLoadedData/onCanPlay trước khi hiển thị WorkspaceNavigator. 3. Thêm hiệu ứng filter blur(7px) brightness(0.92) cho video nền trong app-container/index.tsx và xóa vệt sao băng tĩnh trên ảnh poster. 4. Commit và push lên origin/main.
- [x] 1. Đặt cố định filter blur(8px) brightness(0.95) và lớp phủ rgba(10, 12, 18, 0.32) tại UnauthenticatedWorkspaceBackdrop (app-container/index.tsx). 2. Bỏ lớp backdropFilter: blur(8px) trùng lặp ở overlay của SignInDialog (dialogs/sign-in/index.tsx) để khi mở/đóng hộp thoại Sign in, độ mờ và độ sáng nền không bị chồng lên 2 lần. 3. Commit và push lên origin/main.
- [x] Thêm disableAutoFocus vào SignInDialog Modal và cấu hình outline: none / boxShadow: none cho closeButton trong modal/styles.css.ts
- [x] 1. Bỏ <SidebarHeader /> trong packages/frontend/core/src/modules/app-sidebar/views/index.tsx và ẩn SidebarSwitch trong sidebar-switch.tsx. 2. Cập nhật navBodyStyle trong index.css.ts (height: 100%, paddingTop: 12px) để mục Aevum Workspace nằm gọn đẹp ở đầu sidebar. 3. Commit và push lên origin/main.
- [x] 1. Căn giữa nút < Back trong back-button.tsx và authFooter trong share.css.ts. 2. Bọc SignInPanel bằng ResizeObserver + panelHeightWrapper (transition: height 280ms cubic-bezier(0.22, 1, 0.36, 1)) và stepContentAnimated trong sign-in/index.tsx & sign-in/style.css.ts kèm hiệu ứng đóng/mở Modal mượt mà trong modal/styles.css.ts. 3. Cập nhật desktop/pages/index/index.tsx và desktop/dialogs/sign-in/index.tsx để tự động mở modal đăng nhập khi chưa login và chỉ hiển thị bảng chọn Workspace (WorkspaceNavigator) sau khi đã đăng nhập.
- [x] 1. Xóa <div className={navHeaderStyle} /> (cao 52px) còn sót trong AppSidebarFallback và ShellAppSidebarFallback tại packages/frontend/core/src/modules/app-sidebar/views/index.tsx để khi F5 skeleton không bị tụt xuống dưới rồi mới nhảy lên. 2. Commit và push lên origin/main.
- [x] Kiểm tra RootAppSidebar (packages/frontend/core/src/components/root-app-sidebar/index.tsx) và BlockSuite Kanban view preset (blocksuite/affine/data-view/src/view-presets/kanban)
- [x] Tạo tài liệu đặc tả kỹ thuật docs/spec/aevum-workspace-kanban-spec.md và artifact aevum-workspace-kanban-spec.md cho tính năng Kanban trên Sidebar trái (/kanban route + BlockSuite KanbanViewUI)
- [x] Phân tích chi tiết KanbanSingleView (kanban-view-manager.ts), KanbanCard (pc/card.ts), KanbanGroup (pc/group.ts), popCardMenu (pc/menu.ts) và KanbanHotkeysController (pc/controller/hotkeys.ts)
- [x] Cập nhật docs/spec/aevum-workspace-kanban-spec.md và artifact aevum-workspace-kanban-spec.md với kiến trúc 2 phân khu (Bot Harness Board quản lý 10 Agent Profiles + My Custom Boards) hỗ trợ cả Table View và Kanban View
- [x] Cập nhật docs/spec/aevum-workspace-kanban-spec.md và artifact aevum-workspace-kanban-spec.md: tách biệt dữ liệu Bot Board và My Boards theo từng workspaceId + userId để mỗi người dùng/Workspace có bảng Bot và bảng Cá nhân độc lập
- [x] Cập nhật docs/spec/aevum-workspace-kanban-spec.md và artifact aevum-workspace-kanban-spec.md với cơ chế Admin Config Gate và hộp thoại Admin Config để bạn bật/tắt quyền hiển thị Bot / Harness Kanban cho từng người dùng
- [x] Added LAN/Tailscale IPv4 discovery to /api/auth/open-app/sign-in-code and /api/auth/open-app/network-info
- [x] built MobileQrButton modal in sidebar with qr-creator
- [x] added automatic ?aevum_qr_code= exchange in AuthSession.getSession()
- [x] pushed commit ae80efa65f to origin/main
- [x] 1. Tạo AppSidebarKanbanButton (kanban-button.tsx) và gắn vào RootAppSidebar (root-app-sidebar/index.tsx) ngay dưới Journals. 2. Đăng ký route /kanban trong workbench-router.ts. 3. Xuất snapshot dữ liệu thật từ tools/harness_manager.py sang public/harness-backlog.json. 4. Xây dựng trang WorkspaceKanbanPage (desktop/pages/workspace/kanban/index.tsx & index.css.ts) với cổng phân quyền Admin Config (chỉ Admin hoặc người dùng được Admin bật công tắc mới thấy Bot/Harness Board), hỗ trợ đầy đủ 2 chế độ Table & Kanban cho cả Bot/Harness Board (gom theo State hoặc 10 Bot Profiles, kéo thả card) lẫn My Boards cá nhân (cô lập theo workspaceId).
- [x] Updated open-in-app-card.tsx, open-in-app-page.tsx, app-download-button/index.tsx, mobile/dialogs/setting/index.tsx, and copy-as-image.ts to point to https://github.com/baobao0303/Aevum/pulls
- [x] pushed commit to origin/main
- [x] 1. Khi bấm mục Kanban trên thanh Sidebar trái (/kanban), hiển thị Trang Danh sách các Bảng Kanban (gồm khu vực 🤖 Bảng Bot / Harness 10 Agent Profiles khi được Admin cấp quyền và khu vực 👤 Bảng Kanban Cá nhân My Boards của từng workspace). 2. Cho phép lọc danh sách bảng (Tất cả / Bảng Bot Harness / Bảng Cá nhân), tìm kiếm bảng, tạo bảng cá nhân mới (+ Tạo Bảng Cá nhân) và cấu hình quyền Admin (⚙️ Admin Config). 3. Khi click vào 1 bảng cụ thể trong danh sách, chuyển sang màn hình Chi tiết Bảng đó với đầy đủ 2 chế độ Kanban View & Table View, kèm nút '← Danh sách Kanban' trên thanh tiêu đề để quay lại trang danh sách.
- [x] Updated workbench.ts and workbench-root.tsx so sidebarOpen$ defaults to true with 320px width and uses fresh storage key aevumWorkbenchSidebarOpen
- [x] 1. Tầng 1 (/kanban): Hiển thị Data Table theo đúng thiết kế https://ui.shadcn.com/blocks (cột Drag ⋮⋮, Checkbox ☐, Header, Section Type pill, Status pill với icon Done/In Process, Target input, Limit input, Reviewer select dropdown, và menu ⋮). 2. Đầy đủ Thêm / Xóa / Sửa ngay trên Table: nút '+ Add Section / Thêm mới', sửa trực tiếp inline (Status, Target, Limit, Reviewer), sửa qua Modal ('✏️ Chỉnh sửa' trong menu ⋮), nhân bản ('📑 Nhân bản'), xóa từng dòng ('🗑️ Xóa dòng'), và xóa hàng loạt khi chọn Checkbox ('🗑️ Xóa N mục đã chọn'). 3. Phân tách rõ 2 nhóm trong Table: 🤖 Bot / Harness (10 Agent Profiles — chỉ hiện khi Admin Config bật quyền) và 👤 Cá nhân (Sections: Cover page, Table of contents, Executive summary, Technical approach, Design, Capabilities, Integration with existing systems, Innovation and Advantages...). 4. Tầng 2: Click vào cột Header của bất kỳ dòng nào trong Table sẽ mở ra Bảng Kanban chi tiết của mục đó (kèm nút '← Quay lại Bảng (Table)' trên thanh tiêu đề).
- [x] 1. Revert mặc định sidebarOpen$ về false trong workbench.ts và workbench-root.tsx
- [x] 2. Reverse-engineer API thực tế của <EXTERNAL_SCHEDULE_API> (/hrm/api/v1/resource-ticket/get-by-user, get-for-user-participant, resource/overview-schedule, user/profile)
- [x] 3. Tạo Backend Proxy POST /api/auth/open-app/hrm-rent-schedule chống lỗi CORS, gộp lịch tạo & lịch được mời, lọc từ khóa
- [x] 4. Tạo UI HrmRentScheduleSection + HrmScheduleConfigModal gắn trực tiếp vào trang Journals (cả trạng thái chưa tạo doc lẫn đã tạo doc).
- [x] Đồng bộ toàn bộ CSS exports trong kanban/index.css.ts, hoàn thiện Shadcn Data Table 2 tầng (Table -> Click Header mở Kanban Board), đọc và tổng hợp kiến trúc monorepo projects/aevum
- [x] 1. Loại bỏ toàn bộ emoji (📍, 👤, 👥) và thay bằng bộ vector icon đồng nhất từ @blocksuite/icons/rc (PinIcon, UserIcon, MultiPeopleIcon, DateTimeIcon, ResetIcon, SettingsIcon, DualLinkIcon, TodayIcon)
- [x] 2. Tách stylesheet Vanilla Extract (hrm-rent-schedule-panel.css.ts) dùng cssVarV2 của Aevum theo phong cách monochrome/subtle border của shadcn/ui (bỏ các badge màu neon tím/xanh và font monospace lệch chuẩn).
- [x] 1. Gỡ bỏ hoàn toàn DEFAULT_HRM_URL và các chuỗi domain nội bộ khỏi hrm-rent-schedule-panel.tsx và controller.ts
- [x] 2. Chuyển toàn bộ cấu hình URL + Token sang lưu cục bộ trong LocalStorage trình duyệt hoặc biến môi trường EXTERNAL_SCHEDULE_API_URL
- [x] 3. Ẩn hiển thị URL thô trên giao diện chính của trang Journals
- [x] 4. Quét grep xác nhận 0 kết quả nhạy cảm trong toàn bộ codebase và docs.
- [x] Tạo HeaderNotificationButton trong notification-button.tsx, nhúng vào RouteContainer (route-container.tsx) ở góc phải thanh Header và gỡ khỏi RootAppSidebar
- [x] Khôi phục SidebarSwitch trong sidebar-switch.tsx, gắn vào góc trên phải của Sidebar (cạnh UserInfo) và trên thanh Header khi Sidebar đóng
- [x] thêm mục Settings vào AccountMenu (user-info/account-menu.tsx) và gỡ khỏi danh sách dọc trên Sidebar
- [x] Gỡ bỏ onMouseEnter (setHovering(true)) và tooltip trong sidebar-switch.tsx để chỉ đóng/mở Sidebar khi người dùng click trực tiếp
- [x] 1. Tạo kanban-store.ts và các REST API GET/POST /api/auth/open-app/kanban/boards + /api/auth/open-app/kanban/boards/:boardId trong controller.ts
- [x] 2. Cập nhật kanban/index.tsx gọi API List để hiển thị danh sách Kanban boards đã tạo (kèm số cột, số thẻ, tiến độ %, trạng thái, reviewer) và click vào bất kỳ hàng nào để gọi API Detail mở trang Detail Kanban của board đó (bao gồm Board Summary Banner, Columns kéo thả, Cards, Subtasks checklist và Modal chi tiết thẻ)
- [x] 3. Đồng bộ 100% icon @blocksuite/icons/rc theo chuẩn shadcn/ui.
- [x] 1. Cập nhật kanban-store.ts chỉ trả về đúng 2 bảng Kanban thực tế đã tạo (bỏ toàn bộ 11 dòng mẫu Cover page, Table of contents, SLPC Master...)
- [x] 2. Xóa hoàn toàn thanh tab Outline/Bot/Cá nhân (Hình 2), nút Admin Config và modal Giao Task Bot (Hình 4)
- [x] 3. Đồng bộ 100% UI theo chuẩn shadcn/ui monochrome (nút chính nền sáng chữ tối, viền 1px mảnh, không dùng bất kỳ emoji nào, chỉ dùng @blocksuite/icons/rc)
- [x] 4. Click vào bất kỳ hàng nào gọi API Detail mở Detail Kanban gồm Banner thông số, các cột kéo thả (Backlog -> To Do -> In Progress -> In Review -> Done), thẻ công việc và Modal chi tiết thẻ + Checklist.
- [x] 1. Thay toàn bộ thẻ <select> native và menu dòng thủ công bằng KanbanSelect dùng Menu/MenuItem của @affine/component (chống đè chéo và mất popup OS). 2. Đồng nhất kích thước chuẩn Aevum: 28px cho toolbar/bảng inline, 32px cho form modal, 24px cho card footer select, 22px cho badge. 3. Giữ đúng 2 Kanban boards trong bảng API và gỡ bỏ hoàn toàn tab Outline/Bot/Cá nhân.
- [x] 1. Cố định chiều cao bảng (height: 440px) và cột Kanban (height: 460px), thêm sticky thead và vùng cuộn độc lập shadcnTableScroll. 2. Bổ sung thanh phân trang chuẩn shadcn/ui (chọn Số dòng / trang 5/10/20/50, chỉ số Trang X/Y, các nút « ‹ 1 2 › » cao 28px) cho cả Bảng danh sách Kanban và Bảng danh sách thẻ. 3. Thêm @Throttle('default', { limit: 1200 }) vào controller.ts và seed sẵn 2 bảng mặc định để không bao giờ bị trống 0 hàng.
- [x] 1. Kéo chiều cao cố định của bảng shadcnTableContainer (flex: 1, height: calc(100dvh - 140px), minHeight: 560px) và các cột kanbanColumn (height: calc(100dvh - 220px), minHeight: 560px) xuống sát đáy viewport. 2. Gỡ bỏ giới hạn maxWidth: 1240px ở Hình 2 và giảm padding 2 bên xuống 16px đồng bộ toàn trang.
- [x] Exported isWaitingHrmScheduleStatus and useWaitingHrmScheduleDates in hrm-rent-schedule-panel.tsx
- [x] added markedDates support and amber dot indicator to WeekDatePicker
- [x] wired waitingScheduleDates to both top WeekDatePicker and right sidebar Month DatePicker while removing noisy docActivityDates red dots
- [x] Removed DEFAULT_BOARDS_SEED from kanban/index.tsx
- [x] removed buildSeedBoardsForWorkspace default boards and auto-filtered legacy seed IDs in kanban-store.ts
- [x] cleared temp store files and restarted @aevum/server
- [x] 1. Dùng git mv đổi tên thư mục apps/mfe-cdp/src/app/pages/contact thành apps/mfe-cdp/src/app/pages/customers. 2. Cập nhật import trong apps/mfe-cdp/src/app/remote-entry/entry.routes.ts trỏ tới pages/customers. 3. Chạy nx test mfe-cdp (54/54 tests passed) và nx build mfe-cdp thành công.
- [x] Tiếp nhận chỉ định vai trò Supervisor từ User, sẵn sàng phân tích scope, tạo Epic/Task trên Harness DB và điều phối Lead/Peer/QC
- [x] 1. Đổi tên duplicate-contacts-modal -> duplicate-customers-modal (files, selector wicx-duplicate-customers-modal, class DuplicateCustomersModalComponent). 2. Đổi tên create-contact-modal -> create-customer-modal (files, selector wicx-create-customer-modal, class CreateCustomerModalComponent). 3. Đổi tên contact-list -> customer-list (files, selector wicx-customer-list, class CustomerListComponent, template, styles, spec). 4. Cập nhật entry.routes.ts trỏ sang CustomerListComponent. 5. Chạy nx test (54/54 passed) và nx build thành công 100%.
- [x] Cập nhật ~/.paseo/config.json, profiles/supervisor.md, plugins/slpc-lifecycle-hooks/index.server.ts (enforceSupervisorArgonModel), scripts/harness_dashboard.py
- [x] đổi tên phiên Paseo hiện tại thành Supervisor
- [x] đọc toàn bộ 313 work items trong Floci Harness DB
- [x] 1. Cấu hình HARNESS_BACKEND=floci, FLOCI_ENDPOINT=http://100.124.36.46:14566, FLOCI_S3_BUCKET=harness-data, AWS_ACCESS_KEY_ID=test, AWS_SECRET_ACCESS_KEY=test trong packages/backend/server/.env (gitignored, không lộ IP/secret trong code). 2. Cấp quyền Admin (user_features) cho tài khoản admin@aevum.io & baoltb@aevum.app. 3. Tích hợp đọc/ghi trực tiếp bảng harness_work_items từ Floci DynamoDB vào board-floci-harness (415 work items thực tế: New, Accepted, Active, Blocked, Resolved, Closed) và chỉ trả về khi user là Admin.
- [x] Turn N/A ended with outcome=unknown (agentId=None)
- [x] 1. Chuyển thư mục apps/mfe-cdp/src/app/pages/customers sang apps/mfe-crm/src/app/pages/customers. 2. Sao chép và bổ sung file ngôn ngữ cdp.json vào apps/mfe-crm/public/assets/i18n/{vi,en}. 3. Cập nhật mfe-crm entry.routes.ts tải CustomerListComponent cho cả route rỗng và /customers. 4. Cập nhật mfe-cdp entry.routes.ts phụ trách data-raw. 5. Cấu hình app-shell app.routes.ts để /:shopId/customers và /:shopId/crm tải từ mfe-crm, còn /:shopId/customers/data-raw và /:shopId/data-raw tải từ mfe-cdp. 6. Cập nhật app.routes.spec.ts và bmad/architecture.json. 7. Kiểm thử thành công: mfe-crm (36/36 tests passed), mfe-cdp (18/18 tests passed), app-shell (238/238 tests passed) và build thành công 100%.
- [x] 1. Cố định headerBar (flexWrap: nowrap, textOverflow: ellipsis) để các nút trên thanh tiêu đề không bị rớt dòng và cắt đôi khi mở Sidebar bên phải. 2. Chuyển kanbanColumn sang height: 100%, minHeight: 0 và kanbanBoardRow sang width: max-content để 6 cột Kanban luôn vừa khít chiều cao và cuộn ngang mượt khi mở Sidebar phải. 3. Chuyển journalDateCellDotContainer sang position: absolute (bottom: 2px) để dấu chấm cam ở lịch bên phải không đẩy lệch số ngày (như ngày 22).
- [x] 1. Đính chính chính tả: 'Custommer' (thừa chữ m) -> 'Customer' chuẩn tiếng Anh. 2. Tạo và chuyển sang nhánh feature/20261018-DetailCustomerComponent. 3. Cập nhật thẻ span tên khách hàng (fullName) trong customer-list.component.html với class customer-name-link hover:tds-color-text-interactive hover:underline. 4. Bổ sung style .customer-name-link hover trong customer-list.component.scss. 5. Chạy test mfe-crm (36/36 passed) và nx build mfe-crm thành công.
- [x] 1. Tạo S3 bucket s3://harness-data-backup trên Floci (100.124.36.46:14566). 2. Sao lưu toàn bộ file trong s3://harness-data (test.txt) và toàn bộ dữ liệu DynamoDB (harness_work_items.json: 5,377 bản ghi / 8.48MB, harness_stories.json: 70 bản ghi, harness_tools.json: 4 bản ghi, harness_metadata.json: 1 bản ghi) sang s3://harness-data-backup. 3. Xóa sạch dữ liệu trong s3://harness-data (KeyCount=0) và làm trống bảng harness_work_items (Count=0) để bảng Kanban SLPC Harness trống từ đầu.
- [x] 1. Khởi tạo đồng bộ danh sách bảng Kanban ngay từ frame đầu tiên (0ms) qua memoryBoardsCache + localStorage + cấu hình mặc định của bảng Admin Floci Harness. 2. Tự động preload ngầm chi tiết bảng (Detail Kanban) ngay khi tải danh sách để click vào hàng mở ra tức thì không hiện màn hình chờ. 3. Gỡ bỏ hiệu ứng fadeSlideIn trên contentArea gây nháy khi chuyển trang.
- [x] Cài đặt boto3 vào .venv, cấu hình tools/floci_client.py tự nhận diện .venv để kết nối trực tiếp tới http://100.124.36.46:14566 (không dùng local fallback), đọc toàn bộ 70 stories (14 Active, 38 New, 17 Closed, 1 Accepted) trên Floci
- [x] Xóa các tên Reviewer giả lập hardcode (Lead Dev, Peer Dev, Peer Design, Trần Đại Phát, Nguyễn Thanh Phương)
- [x] thêm listActiveUserNames() trong AuthService và buildKanbanReviewers() trong AuthController để lấy danh sách User thực tế từ DB PostgreSQL (Bao Admin, Bao LTB, Dev User, Pro User, Team User) kết hợp 4 role SLPC (Supervisor, Lead, Peer, QC)
- [x] 1. Thu hồi quyền administrator/admin trong bảng user_features PostgreSQL khỏi các tài khoản thường (baoltb@aevum.app, dev@affine.pro, pro@affine.pro, team@affine.pro), chỉ giữ lại cho admin@aevum.io (Bao Admin). 2. Bổ sung isUserAdmin() trong AuthService và cập nhật resolveKanbanAccess() trong AuthController để kiểm tra quyền administrator thực tế từ PostgreSQL. 3. Gỡ bỏ dropdown chuyển đổi quyền thủ công trên thanh công cụ Kanban và khóa hiển thị board-floci-harness ở Frontend chỉ khi đăng nhập bằng admin@aevum.io.
- [x] 1. Cập nhật tên hiển thị trong bảng users PostgreSQL: admin@aevum.io -> Supervisor, baoltb@aevum.app -> Bảo Bảo, team@affine.pro -> Team User
- [x] 2. Cập nhật listActiveUserNames() trả về ['Supervisor', 'Bảo Bảo', 'Team User']
- [x] 3. Cập nhật resolveKanbanAccess() truyền userName của người đang đăng nhập vào createKanbanBoard() và upsertKanbanCard()
- [x] 4. Cập nhật Frontend Kanban (index.tsx) để khi tạo bảng/thẻ mới mặc định gán Reviewer/Assignee là tên tài khoản đang đăng nhập.
- [x] 1. Phân tích kiến trúc App Shell Header (wicx-header) đã có Breadcrumb toàn cục nên thanh Quay lại / Khách hàng / Tên KH trong DetailCustomerComponent bị dư thừa. 2. Tạo Epic #1 và Task #2 trên Floci DynamoDB (harness_work_items) đồng thời đồng bộ sang S3 bucket harness-data. 3. Xoá khối TOP BREADCRUMB / ACTION BAR (dòng 3-20) trong detail-customer.component.html.
- [x] Cập nhật sideOffset từ 36 thành -6 trong NavigationPanelTreeNodeRenameModal (node.tsx) để ô nhập tên thư mục đè đúng lên dòng thư mục đang sửa thay vì bị tụt xuống 36px đè lên dòng Empty folder bên dưới.
- [x] Thêm styles.renamePopover trong node.css.ts và gắn vào NavigationPanelTreeNodeRenameModal (node.tsx) để cỡ chữ trong ô input đổi tên khớp với cỡ chữ fontSm (14px) của các dòng thư mục trên Sidebar.
- [x] Tạo Bug #3 và Task #4 trên Harness DB
- [x] Sửa header.component.html bỏ mt-1 và căn giữa flexbox
- [x] Chạy 21/21 test suites app-shell pass 100%
- [x] Tái cấu trúc HTML trong detail-customer.component.html: div trái col-span-3 (số 1), div phải col-span-9 bọc khối 2 và khối 3 theo tỉ lệ 7:5
- [x] Chạy pass 100% unit tests DetailCustomerComponent
- [x] Cập nhật modalInput và selectTrigger[data-size=modal] trong kanban/index.css.ts lên height 36px
- [x] bổ sung className styles.controlInput + inline height 36px trong kanban/index.tsx để HMR áp dụng tức thì không bị dẹt chiều cao
- [x] Cập nhật WeekDatePicker phát sự kiện aevum:journal-week-cursor khi chuyển tuần
- [x] cập nhật HrmRentScheduleSection lọc theo Ngày DD/MM và Tuần DD/MM - DD/MM (ví dụ Tuần 18/10 - 24/10 chỉ hiện lịch ngày 22/10, loại bỏ lịch 23/09 và 07/10 của các tuần cũ)
- [x] truyền onSelectDate vào BlocksuiteEditorJournalDocTitle
- [x] Cập nhật detail-customer.component.html: Div 2 items-stretch, Cột 3 h-full
- [x] Tích hợp TDSIllustrationModule wi-empty-page cho trạng thái không có lịch hẹn theo node 2162:28756
- [x] Hỗ trợ scroll mượt và thẻ priority badge (Ưu tiên cao/Trung bình/Thấp)
- [x] Viết 7 unit tests pass 100%
- [x] Loại bỏ hoàn toàn các mã màu hex tự do (#...) và Tailwind colors tự do (text/bg/border-neutral/blue/red/green). Thay thế bằng các class semantic chuẩn TDS: tds-color-surface-lowest, tds-color-border-primary/secondary, tds-color-text-primary/secondary/quaternary/placeholder, tds-color-background-success/warning/info/error/neutral-minimal, nút bấm TDSButtonModule (tds-button-outline, tds-button-outline-icon), thanh cuộn tds-panel-scroll. 43/43 unit tests mfe-crm pass 100%.
- [x] 1. Xóa bỏ hoàn toàn attribute inline style= trên banner mua hàng, chuyển sang class Tailwind chuẩn: bg-gradient-to-b from-[#E5AC33] via-[#F35431] to-[#F12711]. 2. Cập nhật host và toàn bộ grid, các div cột (Div 1, Cột 2, Cột 3) và các card bên dưới (Doanh nghiệp, Lịch sử hoạt động, Ghi chú) sang h-full flex-1 min-h-0 items-stretch để kéo dài full 100% chiều cao màn hình, cuộn nội bộ panel bằng tds-panel-scroll. 3. 7/7 unit tests pass 100%.
- [x] 1. Đã import TDSIllustrationModule trong detail-customer.component.ts (dòng 16 & 84). 2. Kiểm tra node Figma 2162:28757 (Card view empty state của Lịch hẹn sắp tới): cập nhật icon tdsi-calendar-check-line, kích thước illustration 240x240, tiêu đề heading-5 'Chưa có lịch hẹn', ẩn nút Tạo lịch hẹn và số đếm khi danh sách trống. 3. 7/7 unit tests pass 100%.
- [x] Đối chiếu 2 luồng CI/CD (.github/workflows/build-images.yml + .github/deployment/node/Dockerfile và .github/workflows/backend-cicd.yml + Dockerfile.backend) cùng StaticFilesResolver (packages/backend/server/src/core/selfhost/static.ts)
- [x] 1. Đã tạo và resolve Task #5 trên Harness DB. 2. Đổi button Tạo lịch hẹn sang color='info' với token Alias/color/border/info (tds-color-border-info, tds-color-text-info). 3. Đổi icon Ghi chú thành tdsi-edit-file-fill chuẩn 100% Figma node 1761:45606. 4. Thiết lập chia đôi chiều cao (50/50 qua flex-1 min-h-0) và khoảng cách gap-2 (8px) cho Cột 3. 5. 43/43 unit tests passed.
- [x] Cập nhật Dockerfile.backend copy dist của @affine/web, @affine/admin, @affine/mobile vào /app/static
- [x] cập nhật .github/workflows/backend-cicd.yml thêm job build-frontend chạy song song với build-backend rồi gộp vào 1 Docker image duy nhất
- [x] bổ sung biến môi trường Floci S3 vào docker-compose.backend.yml
- [x] 1. Đã rà soát toàn bộ textStyle từ Figma node 1723:37494: Body/body-1-semibold (16px/24px/600), Body/body-2-semibold (14px/20px/600), Body/body-2-regular (14px/20px/400), Body/body-3 / Caption (tds-caption-1). 2. Thay thế toàn bộ class tùy tiện text-xs, text-sm, text-base về đúng token TDS: tds-body-1 font-semibold (tiêu đề Lịch hẹn, Ghi chú, title lịch hẹn, số sự kiện heatmap cells), tds-body-2 font-semibold (tên kênh heatmap, người phụ trách, assignee lịch hẹn, author ghi chú), tds-body-2 font-normal (vai trò ghi chú, text hoạt động), tds-caption-1 font-semibold (tags, badge, button nhỏ, thời gian). 3. Tạo Task #6 trên Harness DB và chuyển trạng thái sang Resolved. 4. Chạy unit test mfe-crm: 45/45 test passed.
- [x] Bổ sung job security-secret-scan (quét AWS/Google/GitHub/OpenAI/Slack keys, JWT Bearer token, IP Tailscale/domain nội bộ, file .env và TruffleHog Verified Secret Scan) vào .github/workflows/backend-cicd.yml
- [x] xóa IP mặc định trong docker-compose.backend.yml
- [x] fix 7 lỗi no-floating-promises trong kanban/index.tsx
- [x] commit và push d6939448eb lên https://github.com/baobao0303/Aevum.git (nhánh main)
- [x] Xóa TDSPopoverModule không dùng
- [x] Drag-to-scroll heatmap, thumb drag sync, dynamic activity count generation, vertical scrollbar
- [x] 1. Đổi màu icon Nữ sang Global/color/pink/400 (text-base-pink-400, #F759A8). 2. Sửa bảng hồ sơ theo Hình 3 (tag Đang tương tác border-transparent, avatar người phụ trách bg #FFD6E7 text #C41D7C Minh Đạt, tag kênh nguồn nền trắng viền mỏng). 3. Chuẩn hóa card Doanh nghiệp theo Figma 1761:46073 (nền trắng tds-color-surface-lowest, viền border-secondary, divide-y 3 dòng, icon flag text-base) và thêm 6 mock records test thanh cuộn. 4. Unit tests pass 45/45. Task 7 chuyển sang Resolved.
- [x] 1. Cấu hình Cột 1 (Hồ sơ khách hàng & Doanh nghiệp) cố định 420px (xl:w-[420px] xl:shrink-0 xl:min-w-[420px]). 2. Cấu hình Cột 3 (Lịch hẹn sắp tới & Ghi chú - Hình 2) cố định 541px (xl:w-[541px] xl:shrink-0 xl:min-w-[541px]). 3. Cấu hình Cột 2 (Thông tin mua hàng & Hoạt động) ở giữa co giãn tự động (flex-1 min-w-0). 4. Kiểm thử thực tế trên Chrome DevTools xác nhận col1=420px, col3=541px, col2=431px. 5. Chạy unit tests 47/47 PASS. Task #8 chuyển sang Resolved.
- [x] 1. Đặt background card tds-color-surface-lowest (Alias/color/surface/lowest) và viền 1px tds-color-border-secondary (Alias/color/border/secondary). 2. Cấu hình padding card chính xác 4px 12px (px-3 py-1). 3. Cấu hình mỗi row cao đúng 36px (h-9 flex items-center), typography Body/body-2-regular (tds-body-2 font-normal) và màu tds-color-text-quaternary (Alias/color/text/quaternary #535A67). 4. Khắc phục triệt để lỗi tràn dòng địa chỉ (Hình 5) bằng truncate block w-full kết hợp h-9 flex items-center min-w-0, đảm bảo text luôn 1 dòng duy nhất, kết thúc bằng dấu ba chấm và có tooltip title khi hover. 5. Unit test 47/47 PASS. Task #9 chuyển sang Resolved.
- [x] 1. Giảm width Cột 1 (Hồ sơ & Doanh nghiệp) từ 420px xuống 360px (xl:w-[360px] xl:min-w-[360px]). 2. Giảm width Cột 3 (Lịch hẹn & Ghi chú) từ 541px xuống 380px (xl:w-[380px] xl:min-w-[380px]). 3. Cột 2 ở giữa mở rộng lên ~652px, bổ sung whitespace-nowrap cho hạn sử dụng/trạng thái gói mua hàng, tăng cột Kênh từ w-20 lên w-[88px] (hiển thị trọn vẹn chữ Facebook) và chỉnh min-w heatmap về 560px để hiển thị đủ 8 tháng không bị cắt.
- [x] 1. Thay thế justify-between và text-right trên 9 dòng thông tin khách hàng bằng layout 2 cột căn trái (nhãn w-[144px] shrink-0 + giá trị flex-1 min-w-0 text-left). 2. Dòng Địa chỉ dùng items-start + text-left để rớt dòng Hồ Chí Minh căn thẳng trục dọc bên trái chuẩn Hình 2. 3. Bỏ giới hạn max-w-[190px] trên Email để hiển thị trọn vẹn địa chỉ email dài. 4. Cân chỉnh Cột 1 ở mức 380px để vừa khít 2 cột thông tin mà vẫn giữ Cột giữa rộng 632px không lỗi.
- [x] Xoá đường kẻ ngang (border-t tds-color-border-secondary) ngăn cách giữa Ngày hoạt động cuối và tiêu đề Doanh nghiệp (6) trong detail-customer.component.html
- [x] 1. Ô Ghi chú: Bổ sung focus:ring-0 và focus:border-[#F35431] để loại bỏ box-shadow xanh mặc định của Tailwind forms, giữ duy nhất viền màu cam chuẩn brand. 2. Độ rộng 3 cột: Cột 1 (xl:w-[340px] 2xl:w-[420px]), Cột 2 (flex-1 xl:min-w-[450px]), Cột 3 (xl:w-[370px] 2xl:w-[541px]) giúp không bị bóp nghẹt trên các màn hình phổ biến. 3. Ma trận Heatmap: Tách riêng cột Kênh (w-[84px] shrink-0) ra ngoài scrollable container, đảm bảo không bao giờ bị cuộn che mất chữ kênh (Kênh, Facebook, Zalo, Website, Tổng đài). 4. 47/47 unit tests pass 100%.
- [x] 1. Đổi tag Đã định danh sang nền xanh lá đậm (tds-color-background-success-subtle), chữ và icon trắng (tds-color-text-white), bo góc 4px (rounded-[4px]). 2. Bỏ border-4 trắng và shadow-sm quanh Avatar. 3. Đổi icon mã KH sang xám (tds-color-icon-secondary) và mã [KH-...] sang xanh dương (tds-color-text-info). 4. Đổi nút Chỉnh sửa sang color=info với viền và chữ xanh dương (tds-color-border-info tds-color-text-info). 5. Xoá đường kẻ ngang (border-t) phía dưới cụm Avatar Header.
- [x] 1. Nhập ghi chú: Chuyển hoàn toàn sang TDS component chuẩn gồm tds-input-group và input[tds-input] với prefix/suffix template, tự động quản lý focus ring chuẩn TDS không bị lỗi 2 màu. 2. Button actions: Chuyển toàn bộ button thao tác sang tds-button-flat-icon và tds-button-outline. 3. Màu sắc: Loại bỏ 100% mã hex tùy tiện, dùng token màu TDS (tds-color-border-brand-primary, tds-color-text-info, tds-color-border-info, tds-color-text-success...). 4. Kích thước layout: Đảm bảo đúng chuẩn Cột 1 (420px), Cột 3 (541px), Cột 2 (min-w 480px) và main canvas overflow-x-auto. 5. Unit tests 47/47 suites PASS 100%.
- [x] Cập nhật icon tdsi-input-number-line size-5 (20x20) Alias/color/icon/secondary (tds-color-icon-secondary) và mã khách hàng màu Alias/color/text/interactive (tds-color-text-interactive) font-semibold
- [x] 1. Thay class custom-scrollbar bằng tds-panel-scroll trên khung Timeline chi tiết sự kiện (dòng 367) và các vùng cuộn Doanh nghiệp, Lịch hẹn sắp tới, Ghi chú. 2. Đồng bộ thanh cuộn ngang Heatmap về chiều cao 4px (h-1 tds-scroll-bar-border-radius) theo đúng token --tds-scroll-bar-height-s. 3. Xoá hoàn toàn .custom-scrollbar tự chế và sửa selector :host thành wicx-detail-customer trong detail-customer.component.scss.
- [x] Cập nhật link logo sang CDN https://static-tds-public-projects.tmtco.org/branding-assets/logos/... cho WiPix, TPOS, WiOn trong detail-customer.component.ts và dọn dẹp các file svg cục bộ
- [x] Xóa hover:tds-color-border-neutral-minimalist transition trên grid card sản phẩm mua của khách hàng
- [x] Thay thế thẻ svg inline bằng icon chuẩn TDS tdsi-female-fill với màu Global/color/pink/400 (text-base-pink-400)
- [x] Đã điều chỉnh chiều cao 2 nút về 26px (size=xs và h-[26px]), icon 16x16 (text-base), nút Chỉnh sửa chuẩn Caption/caption-1-semibold và Alias/color/text/info (tds-caption-1 font-semibold tds-color-text-info), nút Xóa chuẩn Alias/color/icon/error (tds-color-icon-error), test pass 47/47
- [x] Đổi kích thước ảnh avatar thành 120x120
- [x] Dùng tds-tag status='success' size='md' với icon tdsi-security-fill
- [x] Đảm bảo 47/47 unit tests pass
- [x] Dùng tds-tag chuẩn TDS cho Kênh nguồn (WiPix, Facebook)
- [x] Đặt chiều cao 20px (h-[20px]), nền tds-color-surface-low, viền 1px tds-color-border-primary
- [x] Chạy test 47/47 unit tests pass
- [x] Dùng tds-tag type='outline' status='success' với tds-color-background-success-minimal và tds-color-text-success
- [x] Đặt chiều cao 20px, viền trong suốt
- [x] Thêm gender vào ContactListItemDto
- [x] Tạo computed customerGender
- [x] Hiển thị tdsi-male-fill text-base-blue-400 cho Nam và tdsi-female-fill text-base-pink-400 cho Nữ
- [x] 47/47 tests pass
- [x] 1. Cập nhật yarn.lock đồng bộ với qr-creator trong packages/frontend/core/package.json (khắc phục lỗi YN0028 ở bước Install Workspace Dependencies / Setup Node.js). 2. Bổ sung script alias affine/af vào root package.json và cập nhật backend-cicd.yml dùng yarn aevum kèm NODE_OPTIONS 8GB. 3. Cập nhật build-package.yml dùng yarn install --immutable cho build-web, đóng gói đủ node_modules/scripts cho build-backend và tải đủ dist cho build-docker. 4. Gỡ cron schedule tự động trên release.yml, copilot-test-automatically.yml và chuyển build-test.yml sang workflow_dispatch.
- [x] 1. Bổ sung event.preventDefault() trong onHeatmapMouseDown ngăn chặn native HTML5 drag/text selection trên ô số. 2. Chuyển cơ chế lắng nghe mousemove và mouseup sang đối tượng window để kéo cuộn mượt mà không bị ngắt quãng khi chuột lệch ra ngoài container. 3. Loại bỏ cdkDropList/cdkDrag ở Header tháng gây chặn kéo cuộn, đồng bộ kéo mượt mà cả Header lẫn các ô bên dưới. 4. Phân biệt chính xác giữa kéo cuộn (deltaX > 4px) và click chọn ô thông thường (onCellClick). 5. Bổ sung 2 bài test kiểm thử hành vi drag-to-scroll và chống kích hoạt nhầm onCellClick (đạt 49/49 unit tests passed 100%).
- [x] 1. Đọc trực tiếp dữ liệu thiết kế từ Figma node 1761:46027 (Tag Kênh nguồn: nền trắng #FFFFFF, viền 1px #DBE0E6, chữ #656D7C semibold 13px, bo góc 4px, cao 20px). 2. Chuyển tds-tag sang type='outline' status='default' và bọc text bên trong span có màu tds-color-text-secondary (#656D7C) để loại bỏ hoàn toàn việc bị SCSS mặc định của tds-tag ép chữ màu trắng trên nền sáng. 3. Áp dụng viền #DBE0E6 (Alias/color/border/primary) và bo góc chuẩn 4px. 4. Đạt 49/49 unit tests passed 100%.
- [x] 1. Áp dụng class tds-body-3 font-semibold (13px, lineHeight 16px, weight 600) cho chữ hiển thị trạng thái khách hàng trong detail-customer.component.html:L78. 2. Xác nhận 49/49 unit tests pass 100%.
- [x] 1. Ran unit tests (49/49 pass), committed and pushed feature/20261018-DetailCustomerComponent to origin (wicx-crm-fe). 2. Verified Aevum GitHub Actions Build Package #17 and Full-Stack CI/CD #8 passed 100% on origin/main (aab01d5).
- [x] Thay mã hex hardcode bằng token TDS (bg-tds-color-pink-100-light, text-tds-color-pink-600-light và dark mode tương ứng), chuẩn kích thước 24x24 theo Figma 1761:46037, thêm getAssigneeInitial hiển thị chữ cái Đ cho Minh Đạt
- [x] 49/49 unit tests pass 100%
- [x] Đã cập nhật class và SCSS cho button Chỉnh sửa để khoảng cách (gap/margin) giữa prefix icon và text là 4px chuẩn Figma
- [x] Đã áp dụng các token chuẩn TDS tds-body-2 font-normal tds-font-weight-regular tds-color-text-secondary cho toàn bộ 9 dòng nhãn trong bảng key-value thông tin khách hàng
- [x] Đã áp dụng các token chuẩn TDS tds-body-2 font-semibold tds-font-weight-semibold tds-color-text-primary cho toàn bộ các giá trị thuộc cột bên phải trong bảng key-value thông tin khách hàng
- [x] Đã áp dụng tds-body-2 font-semibold tds-font-weight-semibold tds-color-text-primary cho tiêu đề Doanh nghiệp ({{ companies().length }}) và tên doanh nghiệp (comp.name) trong card Doanh nghiệp
- [x] Cập nhật gap 16px (gap-4), icon tdsi-flag-fill size-4 tds-color-icon-tertiary, title Body/body-2-semibold tds-color-text-primary
- [x] Cập nhật tds-color-text-quaternary và tds-body-2 font-normal cho role/phone và address của doanh nghiệp
- [x] 1. Đổi kích thước khung logo gói sản phẩm từ size-7 (28x28px, p-0.5) lên size-[42px] (42x42px, bỏ p-0.5) chuẩn Figma node 1753:43157. 2. Căn giữa theo trục ngang (items-center gap-2) và khoảng cách 2 dòng text gap-0.5 (2px). 3. Chạy 49/49 unit tests pass 100%.
- [x] Thêm draggable cho ô có giá trị, các sự kiện dragstart, dragover, dragleave, drop, dragend
- [x] di chuyển/hoán đổi giá trị giữa các ô và cập nhật selectedCell
- [x] viết 2 unit tests đạt 51/51 passed
- [x] 1. Bổ sung icon Vector watermark 145x145 (left-[44px] -top-[7px], fill=white fill-opacity=0.1) từ Figma node 1753:43151 vào góc phải trên của banner Thông tin mua hàng. 2. Tách 3 cụm nội dung (Thông tin mua hàng / Tổng giá trị đã mua 12.000.000 đ gạch chân đ / Đã hết hạn: 1 gói) với justify-between, p-4, w-[169px] và border-t border-white khớp 100% Hình 1 (node 1723:39867). 3. Chạy 49/49 unit tests pass 100%.
- [x] Thiết lập purchase-info-card chiều cao 344px (md:h-[344px]), căn chỉnh grid 2x2 các gói sản phẩm và banner cam
- [x] Thiết lập width 520px (w-[520px]) cho purchase-info-card và Cột 2, chuyển Cột 3 thành flex-1 (Fill)
- [x] Đối chiếu toàn bộ node Figma 1723:38747
- [x] Chuẩn hóa kích thước ô heatmap 60x32px, gap 12px
- [x] Cập nhật 10 tháng và 4 mã màu kênh chuẩn Figma
- [x] Căn chỉnh indicator bar 4px, typography tabs Body/body-2-semibold, info hint Body/body-2-regular, timeline sự kiện
- [x] Chạy pass 51/51 tests
- [x] Cập nhật HTML và SCSS thiết lập width 541px (min-width 541px, shrink-0 trên màn hình xl) cho Cột 3
- [x] Kiểm thử pass 51/51 unit tests
- [x] Cập nhật icon header thành tds-color-icon-secondary kích thước 16x16
- [x] Kiểm tra Lịch hẹn sắp tới là Body/body-1-semibold (hình 1)
- [x] Kiểm tra (4 lịch hẹn) là Body/body-2-regular Alias/color/text/secondary (hình 2)
- [x] Cập nhật button Tạo lịch hẹn size xs (26px height), border Alias/color/border/info, background Alias/color/surface/low (#FFFFFF), icon 16x16, gap 4px (hình 3)
- [x] Cập nhật border và background card item (#F5F8FB, border #DBE0E6, rounded-[6px])
- [x] Cập nhật priority tag đúng chuẩn Figma (border màu + background mềm)
- [x] Cập nhật nút Chỉnh sửa màu cam (#FA541C), nút Xóa màu đỏ (#F5222D)
- [x] Cập nhật Avatar cam chữ trắng (bg-[#FA541C] text-white)
- [x] Loại bỏ border-t ngăn cách thừa
- [x] 1. Đổi nhãn tab thứ 2 thành Lịch sử cập nhật và ẩn dòng nhắc Bấm vào các ô để xem lịch sử khi ở tab này theo đúng Figma 1753:43668. 2. Xây dựng giao diện timeline nhóm theo ngày (Hôm nay / 30/09/2026) có nút thu gọn/mở rộng (tdsi-arrow-down-fill / tdsi-arrow-right-fill). 3. Hiện thực đầy đủ cột trái (icon tròn 32x32 nền #FDF5F3 với tdsi-user-line, tdsi-calendar-check-line, tdsi-edit-file-line màu #F35431 + đường kẻ dọc nét đứt #DBE0E6) và cột phải (tiêu đề, thời gian, các trường thay đổi Trước → Sau, nút Xem thêm / Rút gọn thông tin / Xem chi tiết, và avatar + tên người cập nhật Minh Đạt / Bùi Thu Trang / Đặng Thái Đình Lâm). 4. Bổ sung unit test cho Lịch sử cập nhật, đạt 52/52 tests pass 100%.
- [x] 1. Gỡ bỏ cố định xl:w-[520px] xl:shrink-0 trên Cột 2 và max-w-[520px] / width: 520px trên .purchase-info-card, chuyển sang flex-1 min-w-0 w-full để cột giữa tự động giãn full 100% chiều ngang phần trống. 2. Chạy 52/52 unit tests pass 100%.
- [x] 1. Đã cập nhật ma trận Heatmap: loại bỏ hardcoded bg-[#F2F5F8] và border-[#DBE0E6], bổ sung dark:bg-[#22262D] và dark:border-[#3A404B], tinh chỉnh màu chữ từng kênh trong dark mode. 2. Loại bỏ transition background/border gây trễ/chớp khi toggle theme, chỉ giữ transition-transform khi drag. 3. Thêm scoped CSS cho .note-input-field với dark:bg-[#181C22], dark:border-[#3A404B], dark:text-[#F2F5F8] và transition: none để triệt tiêu hoàn toàn hiện tượng chớp/chói. 4. Đồng bộ dark mode cho timeline, slider track và card Lịch hẹn. 5. Chạy test mfe-crm đạt 52/52 pass 100%.
- [x] 1. Chuyển runs-on: ubuntu-22.04 cho job build-backend trong .github/workflows/backend-cicd.yml và build-package.yml (biên dịch server-native.x64.node với GLIBC 2.35 tương thích node:22-bookworm-slim GLIBC 2.36)
- [x] 2. Bổ sung include-hidden-files: true vào step Upload Backend Package Artifact (actions/upload-artifact@v4) để giữ nguyên node_modules/.prisma và node_modules/.bin
- [x] 3. Bổ sung symlink ln -s /app/node_modules /node_modules, khôi phục quyền thực thi +x cho prisma engines/bin và chạy prisma generate trong Dockerfile.backend & .github/deployment/node/Dockerfile
- [x] 4. Commit 48dd2e6b77 và push lên origin/main
- [x] 1. Đổi focus:tds-color-border-brand-primary sang focus:border-[#F35431] focus:ring-1 focus:ring-[#F35431] và hover:text-[#F35431] trong detail-customer.component.html
- [x] 2. Bổ sung rule SCSS !important cho .note-input-field với border-color: #F35431, box-shadow: 0 0 0 1px #F35431, triệt tiêu hoàn toàn viền xanh của @tailwindcss/forms ở cả Light và Dark mode
- [x] 3. Chạy 52/52 unit tests pass 100%
- [x] 1. Loại bỏ toàn bộ mã màu hex hardcode trong detail-customer.component.{html,ts,scss}, khôi phục hoàn toàn các class semantic chuẩn TDS (tds-color-*). 2. Sửa thanh cuộn ngang Heatmap (#sliderTrack + .slider-thumb) đồng bộ 2 chiều qua [style.left.px]=sliderThumbLeft(), onThumbMouseDown, onTrackClick, onHeatmapWheel và mở rộng 16 tháng để luôn cuộn mượt trên màn hình rộng. 3. Bổ sung đầy đủ các class màu icon chuẩn TDS (tds-color-icon-info cho tdsi-info-line và nút Edit, tds-color-icon-error cho nút Delete, tds-color-icon-secondary cho tdsi-calendar-check-line, tdsi-edit-file-fill, tdsi-keyboard-return-fill, tdsi-time-1-line, tdsi-arrow-down-fill). 4. Pass 14/14 unit tests và build thành công mfe-crm.
- [x] 1. Đổi getPriorityBadgeClass('Ưu tiên cao') trả về tds-color-background-primary-minimal tds-color-text-brand-primary (Alias/color/background/primary/minimal & Alias/color/text/brand-primary)
- [x] 2. Bỏ class border và đặt height 16px (16 Hug) trong detail-customer.component.html
- [x] 3. Cập nhật unit test trong detail-customer.component.spec.ts và chạy pass 52/52 tests (100%)
- [x] Khôi phục gradient chuẩn Figma (from-[#E5AC33] via-[#F35431] via-[67%] to-[#F12711] và .purchase-banner-gradient) cùng biến --tds-color-primary-500-light cho khối Thông tin mua hàng trong detail-customer.component.html và detail-customer.component.scss.
- [x] 1. Gắn trực tiếp gradient chuẩn Figma (linear-gradient(180deg, #E5AC33 0%, #F35431 67%, #F12711 100%)) và hình watermark lên banner Thông tin mua hàng bên trái. 2. Bổ sung thanh tiến độ 4px (h-1 rounded-full tds-color-background-neutral-minimalist với thanh đỏ 100% tds-color-background-error-subtle cho gói Đã hết hạn và thanh xanh 39% tds-color-background-success-subtle cho gói Còn 117 ngày) cùng nhãn trạng thái dạng chữ (tds-color-text-error / tds-color-text-success) và bóng đổ Shadow/s trên 4 card gói sản phẩm đúng chuẩn Figma 1761:46168.
- [x] Loại bỏ class border tds-color-border-primary ghi đè lên tds-color-border-brand-primary trên thẻ Hồ sơ khách hàng (Div 1), chỉ giữ border-t-4 tds-color-border-brand-primary đúng theo strokeWeight 4px 0px 0px 0px của Figma.
- [x] 1. Đặt chiều rộng thẻ Hồ sơ khách hàng (Div 1) thành 402px (xl:w-[402px] xl:min-w-[402px] và .customer-profile-card width: 402px). 2. Sửa .customer-profile-card border-top thành 4px solid rgb(var(--tds-color-primary-500-light)) (do biến --tds-color-primary-500-light trong theme.all.scss lưu dạng RGB triplet 243,84,49) kết hợp border-t-tds-border-width-xl tds-color-border-brand-primary.
- [x] 1. Gán gender: male cho khách hàng Mai Xuân Thắng (c120) và đầy đủ mock contacts. 2. Nâng cấp bộ nhận diện tên tiếng Việt trong customerGender() của detail-customer.component.ts. 3. Đảm bảo icon nam hiển thị tdsi-male-fill với màu Global/color/sky/400 (text-tds-color-sky-400-light dark:text-tds-color-sky-400-dark). 4. Unit test mfe-crm pass 52/52 (100%).
- [x] 1. Đổi gap-3 sang gap-4 (16px) cho customer-profile-card theo đúng AutoLayout Figma (#1761:46005 gap: 16px). 2. Loại bỏ pt-1 dư thừa ở bảng thông tin và khối Doanh nghiệp liên kết để đảm bảo khoảng cách chuẩn xác đúng 16px. 3. Chạy 52/52 unit tests pass 100%.
- [x] 1. Cập nhật AuthService.isUserAdmin() và listActiveUserNames() trong packages/backend/server/src/core/auth/service.ts tự động gán quyền administrator và tên Supervisor cho admin@aevum.io trên Postgres mới
- [x] 2. Cập nhật buildFlociHarnessBoardRecord() trong kanban-store.ts và fetchBoardsList() trong kanban/index.tsx luôn giữ bảng SLPC Harness — Floci DynamoDB cho Admin
- [x] 3. Khởi động lại @aevum/server và kiểm chứng API trả về bảng SLPC Harness — Floci DynamoDB (10 cards, 90% hoàn thành)
- [x] Cleared custom SCSS rules in customer-list.component.scss and detail-customer.component.scss
- [x] updated customer-list.component.html and detail-customer.component.html to use pure standard TDS components (tds-button, tds-tag, tds-popover, tds-tabset) and TDS Tailwind utility tokens
- [x] Thay thế toàn bộ class primitive -light/-dark (text-tds-color-sky-800-light, bg-tds-color-pink-100-light, bg-tds-color-primary-50-light, bg-tds-color-sky-700-light, from-tds-color-amber-500-light...) và class sai tên (tds-color-background-brand-minimal) bằng các class chuẩn TDS Alias (tds-color-text-interactive-visited, tds-color-background-error-minimal, tds-color-text-error, tds-color-background-primary-minimal, tds-color-background-primary-subtle, tds-color-background-info-subtle-pressed, tds-color-surface-lowest, tds-color-icon-info, tds-color-icon-error)
- [x] 52/52 unit tests PASS
- [x] Cập nhật tableColumns trong customer-list.component.ts đặt tdsChecked: true cho toàn bộ 12 cột (bao gồm Email, Loại khách hàng, Ngày HĐ cuối) và đồng bộ dt.listOfColumn trong updateTableWidthConfig()
- [x] Tách riêng key 'border-dashed': val === null và loại bỏ các class trùng lặp giữa các key trong [ngClass] của ô Heatmap tại detail-customer.component.html để Angular NgClass không tự xóa class border-dashed khi isCellDragOver bằng false
- [x] Bỏ group-hover:tds-color-text-brand-primary ở cột Ghi chú
- [x] thêm tds-modal Lịch sử ghi chú (width 500px, danh sách lịch sử ghi chú chuẩn TDS theo Figma 1318:14221) khi click vào icon/nội dung ghi chú
- [x] Tạo WI-11: Chuẩn hóa Tag Ưu tiên cao (nền primary/minimal, chữ brand-primary, không viền)
- [x] Tạo WI-12: Nhận diện giới tính Nam và hiển thị icon tdsi-male-fill màu Global/color/sky/400
- [x] Tạo WI-13: Cấu hình khoảng cách 16px (gap-4) giữa bảng thông tin và Doanh nghiệp liên kết theo Figma 1761:46005
- [x] Tạo WI-14: Tích hợp Modal Lịch sử ghi chú (500px) và tối ưu tương tác ô Ghi chú
- [x] Tạo WI-15: Hiển thị mặc định 12 cột bảng Khách hàng và chuẩn hóa SCSS sang TDS token

---

## 3. Những Mục Còn Thiếu / Đang Chờ Thực Hiện (Missing & Pending Items)

- [ ] **[M1]** [Máy trạm] Chưa có binary `codex` (`npm install -g @openai/codex`) trên PATH.
- [ ] **[M2]** [Máy trạm] Chưa khởi tạo thư mục gốc `~/.codex` cùng 5 tài nguyên bắt buộc (`config.toml`, `auth.json`, `AGENTS.md`, `skills/`, `plugins/`).
- [ ] **[M3]** [Máy trạm] Chưa clone & build Paseo `v0.8.0` tại `~/projects/supervisors/paseo` và chưa có symlink `~/.local/bin/paseo` (có thể chạy ngay bằng `./scripts/install-paseo`).
- [ ] **[M4]** [Máy trạm] Chưa xuất bản 9 file cấu hình Codex Room (`~/.config/codex-room/*`, `~/.local/bin/codex-room*`, `~/.paseo/config.json`) và 3 thư mục `~/.codex-runtime/{supervisor,lead,peer}` qua `./install --apply`.
- [ ] **[M5]** [Daemon] Paseo Daemon chưa khởi chạy ở `127.0.0.1:6767` nên chưa chạy bước kiểm chứng live (`./install --verify --live`).
- [ ] **[M6]** Chờ phản hồi hoặc yêu cầu tiếp theo từ User
- [ ] **[M7]** Có thể mở rộng thêm UI Nâng cấp công trình, Chế tạo vũ khí, Sinh thú dữ/chiến đấu và nối đủ 12 màn chơi chiến dịch nếu User yêu cầu
- [ ] **[M8]** Chờ User xác nhận duyệt prompt_draft.md để gọi invoke_subagent(teamwork_preview)
- [ ] **[M9]** Milestone M2 (Buildings Catalog, Scaffolding, Upgrades, Crafting & Traps)
- [ ] **[M10]** Milestone 2 buildings, tech tree, weapon crafting, and traps
- [ ] **[M11]** Tiến hành Milestone 2: 12 Công trình 3D, Nâng cấp 3 cấp độ, Chế tạo vũ khí & Cạm bẫy
- [ ] **[M12]** Milestones 2-5 (12 3D Buildings, 3D Villagers/Beasts/Raiders, 4-Chapter Campaign & Full HUD) in progress via teamwork_preview subagent
- [ ] **[M13]** None for Milestone 2
- [ ] **[M14]** None for M3
- [ ] **[M15]** m4_worker_1 is actively writing GlassmorphicHUD.ts and wiring src/main.ts right now
- [ ] **[M16]** None for Milestone 4.
- [ ] **[M17]** None
- [ ] **[M18]** None — all gates and Victory Audit passed.
- [ ] **[M19]** Chờ User tương tác trên UI browser
- [ ] **[M20]** Chờ User trải nghiệm và phản hồi trên browser UI
- [ ] **[M21]** Bàn giao cho Lead và Peer triển khai tích hợp
- [ ] **[M22]** Cho Peer hoan thanh Task #286 (affine-crdt voi y-octo va zstd compaction)
- [ ] **[M23]** Chờ User trải nghiệm trên http://127.0.0.1:3000
- [ ] **[M24]** Không còn hạng mục thiếu.
- [ ] **[M25]** Không còn hạng mục thiếu
- [ ] **[M26]** Không
- [ ] **[M27]** Không còn hạng mục tồn đọng
- [ ] **[M28]** Chờ User xác nhận có muốn gắn mục Kanban lên trực tiếp thanh Sidebar trái hay không
- [ ] **[M29]** Chờ User xem duyệt spec và nhấn Proceed để triển khai code
- [ ] **[M30]** Chờ User xác nhận triển khai mục Kanban trên Sidebar trái
- [ ] **[M31]** Chờ User duyệt kế hoạch 4 bước để bắt tay vào code
- [ ] **[M32]** Chờ User duyệt để bắt tay vào code
- [ ] **[M33]** Không có
- [ ] **[M34]** Không còn
- [ ] **[M35]** Chờ yêu cầu nghiệp vụ/task từ User
- [ ] **[M36]** QC nghiệm thu và đóng Bug #3 / Task #4
- [ ] **[M37]** QC nghiệm thu layout
- [ ] **[M38]** QC nghiệm thu các trường hợp hiển thị
- [ ] **[M39]** Không còn hạng mục thiếu cho yêu cầu này.
- [ ] **[M40]** Không còn thiếu sót nào về chuẩn typography token trên màn hình.
- [ ] **[M41]** Không còn thiếu sót nào theo yêu cầu.
- [ ] **[M42]** Không còn hạng mục nào tồn đọng.
- [ ] **[M43]** Không còn thiếu sót nào
- [ ] **[M44]** Tiếp tục review UI theo thiết kế TDS nếu user yêu cầu
- [ ] **[M45]** Chờ phản hồi tiếp theo từ user
- [ ] **[M46]** Đang chờ GitHub Actions chạy xác nhận trên nhánh main
- [ ] **[M47]** Chờ GitHub Actions hoàn tất build và push image ghcr.io/baobao0303/aevum-backend:latest

---

## 4. Nhật Ký Bàn Giao Phiên Làm Việc (Session Handoff Log)

> Lưu ý: Hiển thị 20 phiên gần nhất (tổng số: 270 phiên được lưu trong `.harness_progress.json`).

### Phiên #270 — `2026-10-19 00:08:30 +0700` | **Supervisor**
- **Tóm tắt**: Đã đồng bộ và tạo bổ sung 5 Tasks (WI-11 đến WI-15) trên Harness Floci DynamoDB cho các hạng mục fix gần nhất và cập nhật trạng thái Resolved
- **Đã thực hiện**:
  - Tạo WI-11: Chuẩn hóa Tag Ưu tiên cao (nền primary/minimal, chữ brand-primary, không viền)
  - Tạo WI-12: Nhận diện giới tính Nam và hiển thị icon tdsi-male-fill màu Global/color/sky/400
  - Tạo WI-13: Cấu hình khoảng cách 16px (gap-4) giữa bảng thông tin và Doanh nghiệp liên kết theo Figma 1761:46005
  - Tạo WI-14: Tích hợp Modal Lịch sử ghi chú (500px) và tối ưu tương tác ô Ghi chú
  - Tạo WI-15: Hiển thị mặc định 12 cột bảng Khách hàng và chuẩn hóa SCSS sang TDS token
- **File đã tạo/cập nhật**: `tools/harness_manager.py`, `docs/AGENT_PROGRESS.md`
- **Bàn giao bước tiếp theo**: Chờ User kiểm tra lại bảng Kanban trên giao diện Aevum và nghiệm thu giao diện DetailCustomerComponent

### Phiên #269 — `2026-10-19 00:05:49 +0700` | **Peer**
- **Tóm tắt**: Bỏ đổi màu cam khi hover cột Ghi chú và mở modal Lịch sử ghi chú (Figma 1318:14221) khi click
- **Đã thực hiện**:
  - Bỏ group-hover:tds-color-text-brand-primary ở cột Ghi chú
  - thêm tds-modal Lịch sử ghi chú (width 500px, danh sách lịch sử ghi chú chuẩn TDS theo Figma 1318:14221) khi click vào icon/nội dung ghi chú
  - 52/52 unit tests PASS
- **File đã tạo/cập nhật**: `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/customer-list/customer-list.component.html`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/customer-list/customer-list.component.ts`
- **Bàn giao bước tiếp theo**: Chờ User kiểm tra giao diện trên trình duyệt

### Phiên #268 — `2026-10-19 00:00:26 +0700` | **Peer**
- **Tóm tắt**: Fix mất đường viền nét đứt (border-dashed) ở các ô trống trong Heatmap
- **Đã thực hiện**:
  - Tách riêng key 'border-dashed': val === null và loại bỏ các class trùng lặp giữa các key trong [ngClass] của ô Heatmap tại detail-customer.component.html để Angular NgClass không tự xóa class border-dashed khi isCellDragOver bằng false
- **File đã tạo/cập nhật**: `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.html`
- **Bàn giao bước tiếp theo**: Chờ User kiểm tra giao diện trên trình duyệt

### Phiên #267 — `2026-10-18 23:57:18 +0700` | **Peer**
- **Tóm tắt**: Bật hiển thị đầy đủ 12 cột mặc định trên tab Tất cả của trang danh sách khách hàng
- **Đã thực hiện**:
  - Cập nhật tableColumns trong customer-list.component.ts đặt tdsChecked: true cho toàn bộ 12 cột (bao gồm Email, Loại khách hàng, Ngày HĐ cuối) và đồng bộ dt.listOfColumn trong updateTableWidthConfig()
  - 52/52 unit tests PASS
- **File đã tạo/cập nhật**: `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/customer-list/customer-list.component.ts`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/customer-list/customer-list.component.spec.ts`
- **Bàn giao bước tiếp theo**: Chờ User kiểm tra giao diện trên trình duyệt

### Phiên #266 — `2026-10-18 23:54:17 +0700` | **Peer**
- **Tóm tắt**: Chuẩn hóa toàn bộ class bg/text/icon trong detail-customer.component.html và detail-customer.component.ts sang 100% TDS Alias classes
- **Đã thực hiện**:
  - Thay thế toàn bộ class primitive -light/-dark (text-tds-color-sky-800-light, bg-tds-color-pink-100-light, bg-tds-color-primary-50-light, bg-tds-color-sky-700-light, from-tds-color-amber-500-light...) và class sai tên (tds-color-background-brand-minimal) bằng các class chuẩn TDS Alias (tds-color-text-interactive-visited, tds-color-background-error-minimal, tds-color-text-error, tds-color-background-primary-minimal, tds-color-background-primary-subtle, tds-color-background-info-subtle-pressed, tds-color-surface-lowest, tds-color-icon-info, tds-color-icon-error)
  - 52/52 unit tests PASS
- **File đã tạo/cập nhật**: `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.html`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.ts`
- **Bàn giao bước tiếp theo**: Chờ User kiểm tra giao diện trên trình duyệt

### Phiên #265 — `2026-10-18 23:47:12 +0700` | **Peer**
- **Tóm tắt**: Removed custom SCSS overrides from customer-list.component.scss and detail-customer.component.scss, replacing with standard TDS components and tokens
- **Đã thực hiện**:
  - Cleared custom SCSS rules in customer-list.component.scss and detail-customer.component.scss
  - updated customer-list.component.html and detail-customer.component.html to use pure standard TDS components (tds-button, tds-tag, tds-popover, tds-tabset) and TDS Tailwind utility tokens
- **File đã tạo/cập nhật**: `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/customer-list/customer-list.component.scss`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/customer-list/customer-list.component.html`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.scss`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.html`
- **Bàn giao bước tiếp theo**: User visual verification

### Phiên #264 — `2026-10-18 23:46:07 +0700` | **Peer**
- **Tóm tắt**: Tự động cấp quyền administrator và tên Supervisor cho admin@aevum.io trên DB Postgres mới (100.124.36.46:5432), đảm bảo bảng SLPC Harness — Floci DynamoDB luôn hiển thị
- **Đã thực hiện**:
  - 1. Cập nhật AuthService.isUserAdmin() và listActiveUserNames() trong packages/backend/server/src/core/auth/service.ts tự động gán quyền administrator và tên Supervisor cho admin@aevum.io trên Postgres mới
  - 2. Cập nhật buildFlociHarnessBoardRecord() trong kanban-store.ts và fetchBoardsList() trong kanban/index.tsx luôn giữ bảng SLPC Harness — Floci DynamoDB cho Admin
  - 3. Khởi động lại @aevum/server và kiểm chứng API trả về bảng SLPC Harness — Floci DynamoDB (10 cards, 90% hoàn thành)
- **File đã tạo/cập nhật**: `projects/aevum/packages/backend/server/src/core/auth/service.ts`, `projects/aevum/packages/backend/server/src/core/auth/kanban-store.ts`, `projects/aevum/packages/frontend/core/src/desktop/pages/workspace/kanban/index.tsx`
- **Bàn giao bước tiếp theo**: Chờ phản hồi từ User

### Phiên #263 — `2026-10-18 23:37:40 +0700` | **Peer**
- **Tóm tắt**: Chuẩn hóa khoảng cách 16px giữa bảng thông tin khách hàng và mục Doanh nghiệp liên kết
- **Đã thực hiện**:
  - 1. Đổi gap-3 sang gap-4 (16px) cho customer-profile-card theo đúng AutoLayout Figma (#1761:46005 gap: 16px). 2. Loại bỏ pt-1 dư thừa ở bảng thông tin và khối Doanh nghiệp liên kết để đảm bảo khoảng cách chuẩn xác đúng 16px. 3. Chạy 52/52 unit tests pass 100%.
- **File đã tạo/cập nhật**: `apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.html`
- **Bàn giao bước tiếp theo**: Chờ phản hồi tiếp theo từ user

### Phiên #262 — `2026-10-18 23:32:45 +0700` | **Peer**
- **Tóm tắt**: Chuẩn hóa icon giới tính nam tdsi-male-fill và màu Global/color/sky/400
- **Đã thực hiện**:
  - 1. Gán gender: male cho khách hàng Mai Xuân Thắng (c120) và đầy đủ mock contacts. 2. Nâng cấp bộ nhận diện tên tiếng Việt trong customerGender() của detail-customer.component.ts. 3. Đảm bảo icon nam hiển thị tdsi-male-fill với màu Global/color/sky/400 (text-tds-color-sky-400-light dark:text-tds-color-sky-400-dark). 4. Unit test mfe-crm pass 52/52 (100%).
- **File đã tạo/cập nhật**: `apps/mfe-crm/src/app/pages/customers/services/customer.service.ts`, `apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.ts`, `apps/mfe-crm/src/app/pages/customers/components/create-customer-modal/create-customer-modal.component.ts`
- **Bàn giao bước tiếp theo**: Chờ phản hồi tiếp theo từ user

### Phiên #261 — `2026-10-18 23:31:00 +0700` | **Peer**
- **Tóm tắt**: Cập nhật width 402px và sửa lỗi biến CSS RGB cho đường viền cam 4px trên thẻ Hồ sơ khách hàng
- **Đã thực hiện**:
  - 1. Đặt chiều rộng thẻ Hồ sơ khách hàng (Div 1) thành 402px (xl:w-[402px] xl:min-w-[402px] và .customer-profile-card width: 402px). 2. Sửa .customer-profile-card border-top thành 4px solid rgb(var(--tds-color-primary-500-light)) (do biến --tds-color-primary-500-light trong theme.all.scss lưu dạng RGB triplet 243,84,49) kết hợp border-t-tds-border-width-xl tds-color-border-brand-primary.
- **File đã tạo/cập nhật**: `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.html`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.scss`
- **Bàn giao bước tiếp theo**: User kiểm tra trên trình duyệt

### Phiên #260 — `2026-10-18 23:26:48 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: User kiểm tra đường kẻ viền cam 4px trên trình duyệt

### Phiên #259 — `2026-10-18 23:26:17 +0700` | **Peer**
- **Tóm tắt**: Khôi phục đường kẻ viền trên 4px Alias/color/border/brand-primary (border-t-4 tds-color-border-brand-primary) trên thẻ Hồ sơ khách hàng
- **Đã thực hiện**:
  - Loại bỏ class border tds-color-border-primary ghi đè lên tds-color-border-brand-primary trên thẻ Hồ sơ khách hàng (Div 1), chỉ giữ border-t-4 tds-color-border-brand-primary đúng theo strokeWeight 4px 0px 0px 0px của Figma.
- **File đã tạo/cập nhật**: `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.html`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.scss`
- **Bàn giao bước tiếp theo**: User kiểm tra đường kẻ viền cam 4px trên trình duyệt

### Phiên #258 — `2026-10-18 23:25:02 +0700` | **Peer**
- **Tóm tắt**: Chuẩn hóa Card 1 (Thông tin mua hàng) theo đúng Figma 1761:46168 trên DetailCustomerComponent
- **Đã thực hiện**:
  - 1. Gắn trực tiếp gradient chuẩn Figma (linear-gradient(180deg, #E5AC33 0%, #F35431 67%, #F12711 100%)) và hình watermark lên banner Thông tin mua hàng bên trái. 2. Bổ sung thanh tiến độ 4px (h-1 rounded-full tds-color-background-neutral-minimalist với thanh đỏ 100% tds-color-background-error-subtle cho gói Đã hết hạn và thanh xanh 39% tds-color-background-success-subtle cho gói Còn 117 ngày) cùng nhãn trạng thái dạng chữ (tds-color-text-error / tds-color-text-success) và bóng đổ Shadow/s trên 4 card gói sản phẩm đúng chuẩn Figma 1761:46168.
- **File đã tạo/cập nhật**: `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.html`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.ts`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.scss`
- **Bàn giao bước tiếp theo**: User kiểm tra giao diện Card Thông tin mua hàng trên trình duyệt

### Phiên #257 — `2026-10-18 23:21:20 +0700` | **Peer**
- **Tóm tắt**: Khôi phục banner gradient cam cho khối Thông tin mua hàng trên DetailCustomerComponent
- **Đã thực hiện**:
  - Khôi phục gradient chuẩn Figma (from-[#E5AC33] via-[#F35431] via-[67%] to-[#F12711] và .purchase-banner-gradient) cùng biến --tds-color-primary-500-light cho khối Thông tin mua hàng trong detail-customer.component.html và detail-customer.component.scss.
- **File đã tạo/cập nhật**: `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.html`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.scss`
- **Bàn giao bước tiếp theo**: User kiểm tra lại banner Thông tin mua hàng trên trình duyệt

### Phiên #256 — `2026-10-18 23:20:59 +0700` | **Peer**
- **Tóm tắt**: Cập nhật style tag 'Ưu tiên cao' sang tds-color-text-brand-primary, tds-color-background-primary-minimal và bỏ hoàn toàn đường viền
- **Đã thực hiện**:
  - 1. Đổi getPriorityBadgeClass('Ưu tiên cao') trả về tds-color-background-primary-minimal tds-color-text-brand-primary (Alias/color/background/primary/minimal & Alias/color/text/brand-primary)
  - 2. Bỏ class border và đặt height 16px (16 Hug) trong detail-customer.component.html
  - 3. Cập nhật unit test trong detail-customer.component.spec.ts và chạy pass 52/52 tests (100%)
- **File đã tạo/cập nhật**: `apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.ts`, `apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.html`, `apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.spec.ts`
- **Bàn giao bước tiếp theo**: Chờ phản hồi tiếp theo từ user

### Phiên #255 — `2026-10-18 23:19:29 +0700` | **Peer**
- **Tóm tắt**: Chuẩn hóa toàn bộ token màu TDS, sửa thanh cuộn ngang Heatmap và bổ sung màu icon theo chuẩn Figma 1753:43436 trên DetailCustomerComponent
- **Đã thực hiện**:
  - 1. Loại bỏ toàn bộ mã màu hex hardcode trong detail-customer.component.{html,ts,scss}, khôi phục hoàn toàn các class semantic chuẩn TDS (tds-color-*). 2. Sửa thanh cuộn ngang Heatmap (#sliderTrack + .slider-thumb) đồng bộ 2 chiều qua [style.left.px]=sliderThumbLeft(), onThumbMouseDown, onTrackClick, onHeatmapWheel và mở rộng 16 tháng để luôn cuộn mượt trên màn hình rộng. 3. Bổ sung đầy đủ các class màu icon chuẩn TDS (tds-color-icon-info cho tdsi-info-line và nút Edit, tds-color-icon-error cho nút Delete, tds-color-icon-secondary cho tdsi-calendar-check-line, tdsi-edit-file-fill, tdsi-keyboard-return-fill, tdsi-time-1-line, tdsi-arrow-down-fill). 4. Pass 14/14 unit tests và build thành công mfe-crm.
- **File đã tạo/cập nhật**: `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.html`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.ts`, `projects/wicx-crm-fe/apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.scss`
- **Bàn giao bước tiếp theo**: User kiểm tra trực tiếp trên giao diện trình duyệt

### Phiên #254 — `2026-10-18 23:17:53 +0700` | **Peer**
- **Tóm tắt**: Loại bỏ hoàn toàn viền/outline xanh khi focus vào ô input Ghi chú, chuẩn hóa màu cam #F35431
- **Đã thực hiện**:
  - 1. Đổi focus:tds-color-border-brand-primary sang focus:border-[#F35431] focus:ring-1 focus:ring-[#F35431] và hover:text-[#F35431] trong detail-customer.component.html
  - 2. Bổ sung rule SCSS !important cho .note-input-field với border-color: #F35431, box-shadow: 0 0 0 1px #F35431, triệt tiêu hoàn toàn viền xanh của @tailwindcss/forms ở cả Light và Dark mode
  - 3. Chạy 52/52 unit tests pass 100%
- **File đã tạo/cập nhật**: `apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.html`, `apps/mfe-crm/src/app/pages/customers/components/detail-customer/detail-customer.component.scss`
- **Bàn giao bước tiếp theo**: Chờ phản hồi tiếp theo từ user

### Phiên #253 — `2026-10-18 23:15:40 +0700` | **Peer**
- **Tóm tắt**: Commit và push bản sửa lỗi 3 vấn đề build Docker/CI của Aevum (48dd2e6b77) lên origin/main
- **Đã thực hiện**:
  - 1. Chuyển runs-on: ubuntu-22.04 cho job build-backend trong .github/workflows/backend-cicd.yml và build-package.yml (biên dịch server-native.x64.node với GLIBC 2.35 tương thích node:22-bookworm-slim GLIBC 2.36)
  - 2. Bổ sung include-hidden-files: true vào step Upload Backend Package Artifact (actions/upload-artifact@v4) để giữ nguyên node_modules/.prisma và node_modules/.bin
  - 3. Bổ sung symlink ln -s /app/node_modules /node_modules, khôi phục quyền thực thi +x cho prisma engines/bin và chạy prisma generate trong Dockerfile.backend & .github/deployment/node/Dockerfile
  - 4. Commit 48dd2e6b77 và push lên origin/main
- **File đã tạo/cập nhật**: `projects/aevum/.github/workflows/backend-cicd.yml`, `projects/aevum/.github/workflows/build-package.yml`, `projects/aevum/Dockerfile.backend`, `projects/aevum/.github/deployment/node/Dockerfile`
- **Bàn giao bước tiếp theo**: Kiểm tra kết quả GitHub Actions và pull image mới trên server port 3010

### Phiên #252 — `2026-10-18 23:11:34 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: Chờ feedback từ người dùng

### Phiên #251 — `2026-10-18 23:05:41 +0700` | **Paseo/Agent**
- **Tóm tắt**: Paseo hook agent.turn_ended (unknown) - session
- **Đã thực hiện**:
  - Turn N/A ended with outcome=unknown (agentId=None)
- **Bàn giao bước tiếp theo**: Chờ feedback từ người dùng

---

## 5. Hướng Dẫn Lệnh Nhanh Cho Agent

```bash
# 1. Xem nhanh báo cáo để trả lời User khi được yêu cầu "làm tiếp":
python3 tools/agent_progress.py status

# 2. Ghi nhận công việc vừa làm xong & cập nhật bước tiếp theo:
python3 tools/agent_progress.py log \
  --agent "Lead Dev" \
  --focus "Trọng tâm công việc hiện tại" \
  --summary "Tóm tắt ngắn gọn phiên làm việc" \
  --done "Việc đã xong 1; Việc đã xong 2" \
  --missing "Việc còn thiếu 1; Việc còn thiếu 2" \
  --next "Bước cụ thể cần làm ngay khi User bảo làm tiếp" \
  --files "docs/spec/file1.md,tools/script2.py"
```
