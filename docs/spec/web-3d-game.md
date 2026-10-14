# Spec: Web 3D Game Hub (Three.js + TypeScript)

Status: DRAFT. Scope assumption below, cần User xác nhận.

## 0. Nguồn & giả định
- Tham chiếu: video "I Built (And Shipped) a 3D Game With Claude Opus 5.5 (Full Workflow)" (https://www.youtube.com/watch?v=3QwU8TM7Rag).
- Nội dung video KHÔNG đọc được (fetch/search chỉ trả title). Spec dựa trên title + yêu cầu User: "tất cả thể loại, chạy web".
- Giả định: 1 game hub, nhiều mini-game 3D, chạy browser, có ship (deploy public).
- Việc cần User: xem video, đối chiếu mục 3, sửa mô tả mini-game nếu lệch.

## 1. Mục tiêu
- Ship bản chơi được trên web, không cài đặt, 1 URL.
- 3 mini-game 3D (platformer/runner, shooter/survival, racing) dùng chung engine core.
- Mỗi mini-game chơi được 1-3 phút/lượt, có điểm, restart ngay.

## 2. Non-goals (v1)
- Multiplayer online.
- Backend/account. Điểm cao lưu `localStorage`.
- Level editor, mod, asset store.
- Native app / mobile build (chỉ responsive touch tối thiểu).

## 3. Mini-game

### 3.1 Runner/Platformer
- Nhân vật chạy tự động theo trục -Z, 3 lane. Input: trái/phải đổi lane, Space nhảy, S/Down lướt.
- Chướng ngại: block thấp (nhảy), block cao (lướt), hố (nhảy).
- Pickup: coin (+10), shield (chặn 1 va chạm), magnet (hút coin 5s).
- Tốc độ tăng dần theo quãng đường.
- Thua: va chạm không shield. Điểm = quãng đường + coin.
- Chunk map sinh procedural, pool tái sử dụng.

### 3.2 Shooter/Survival
- Camera top-down hoặc third-person. WASD di chuyển, chuột ngắm/bắn.
- Enemy theo wave: Chaser (chạy tới, melee), Shooter (bắn từ xa), Tank (HP cao, chậm).
- Wave N: số enemy = `5 + 3*N`. Boss mỗi 5 wave.
- Vũ khí: pistol (mặc định), shotgun, SMG. Drop nhặt trong arena.
- HP 100, hồi bằng health pickup. Thua khi HP = 0. Điểm = kills * hệ số wave.

### 3.3 Racing
- Xe arcade (không sim vật lý đầy đủ). W/S ga/phanh, A/D lái, Space drift.
- 1 track khép kín, 3 lap, checkpoint chống cắt đường.
- 3 xe AI follow spline, rubber-banding nhẹ.
- Kết quả: thứ hạng + best lap time.

### 3.4 Hub
- Menu chọn game, xem điểm cao, cài đặt (âm lượng, chất lượng đồ hoạ, key bind).

## 4. Tech stack
| Lớp | Chọn | Lý do |
|---|---|---|
| Render | three (r16x+) | Chuẩn web 3D |
| Ngôn ngữ | TypeScript strict | An toàn kiểu |
| Build | Vite | Dev nhanh, bundle gọn |
| Physics | `cannon-es` hoặc `@dimforge/rapier3d-compat` | Va chạm; ưu tiên Rapier nếu cần ổn định |
| Audio | Web Audio API / `three` PositionalAudio | Không thêm dep |
| UI/HUD | HTML/CSS overlay | Native, accessible |
| Test | Vitest (logic thuần) | Nhẹ |
| Deploy | Static host (GitHub Pages / Netlify / Cloudflare Pages) | Không backend |

Không dùng: framework game nặng, React Three Fiber (trừ khi User yêu cầu).

## 5. Kiến trúc
```
src/
  core/        # engine dùng chung
    Game.ts        # loop, fixed timestep, state machine
    Input.ts       # keyboard/mouse/touch -> action map
    Assets.ts      # loader + cache (glTF, texture, audio)
    Audio.ts
    Storage.ts     # localStorage wrapper (high score, settings)
  games/
    runner/ shooter/ racing/   # mỗi game: Scene, systems, entities, config
  ui/          # hub menu, HUD, pause, game over
  main.ts
public/assets/ # models (glTF/glb), textures, sfx
```
- Interface `GameModule { init(ctx), update(dt), dispose() }`. Hub load module theo lựa chọn (dynamic import, code-split).
- Fixed timestep 60Hz cho logic, render nội suy.
- Entity đơn giản (class + system), không ECS trừ khi cần.
- `dispose()` giải phóng geometry/material/texture để chuyển game không leak.

## 6. Yêu cầu phi chức năng
- 60 FPS desktop tầm trung; >=30 FPS mobile trung bình.
- Bundle ban đầu (hub) < 1 MB gzip; mỗi game lazy-load.
- Time-to-interactive < 3s trên băng thông 10 Mbps.
- Instancing/pooling cho coin, đạn, enemy.
- Tùy chọn chất lượng: Low/Med/High (shadow, pixel ratio, số particle).
- Accessibility: pause bằng Esc, key rebind, giảm rung camera, không phụ thuộc chỉ màu.
- Pause tự động khi tab mất focus.

## 7. Asset
- Low-poly glTF, CC0 (Kenney, Quaternius) để ship nhanh và tránh vướng bản quyền.
- SFX/nhạc: CC0 (freesound CC0, Kenney audio). Ghi credit trong màn About.
- Nén: Draco/meshopt cho model, KTX2 nếu texture lớn (YAGNI: chỉ khi vượt budget).

## 8. Milestone
| M | Nội dung | Done khi |
|---|---|---|
| M0 | Vite+TS+three scaffold, loop, input, camera, 1 cube | `npm run dev` chạy, 60 FPS |
| M1 | Runner playable | Chơi 1 lượt từ start tới game over, lưu high score |
| M2 | Hub + pause + settings + audio | Chuyển menu <-> game không leak |
| M3 | Shooter playable | 5 wave + boss |
| M4 | Racing playable | 3 lap + AI + best lap |
| M5 | Polish: VFX, SFX, touch, quality presets | Checklist mục 6 đạt |
| M6 | Ship | URL public, README, credit asset |

Thứ tự ship tối thiểu: M0 -> M1 -> M2 -> M6 (runner đã đủ ship). M3/M4 tăng dần.

## 9. Acceptance criteria (v1)
- [ ] Hub load, chọn được 3 game.
- [ ] Mỗi game: start, chơi, thua/thắng, restart, điểm hiển thị.
- [ ] High score persist qua reload.
- [ ] Pause/resume hoạt động; blur tab tự pause.
- [ ] Chuyển game không tăng bộ nhớ liên tục (kiểm `renderer.info`).
- [ ] Build production chạy tĩnh, không lỗi console.
- [ ] Tối thiểu 1 unit test cho logic thuần (scoring, wave spawn, lap tracking).

## 10. Rủi ro
| Rủi ro | Giảm thiểu |
|---|---|
| Scope 3 game quá lớn | Ship runner trước, các game sau là increment |
| Vật lý xe khó chỉnh | Arcade model, không sim lốp |
| Perf mobile | Quality preset, instancing, giới hạn shadow |
| Bản quyền asset | Chỉ CC0, ghi credit |
| Lệch so với video | User đối chiếu mục 3 trước khi code |

## 11. Câu hỏi mở (User quyết)
1. "Tất cả thể loại" = 3 game trên, hay thêm thể loại khác (puzzle, RPG, ...)?
2. Game trong video có mechanic/art style cụ thể cần bám sát?
3. Cần mobile touch ở v1 hay chỉ desktop?
4. Host deploy ưu tiên nơi nào?

## 12. Đặc tả vật thể 3D (procedural, dùng để test model sinh code)

Mục đích: mỗi vật thể mô tả đủ để 1 model sinh ra 1 hàm `createX(): THREE.Group` chạy ngay, không cần asset ngoài. Mục 7 (asset CC0) là phương án thay thế khi polish.

### 12.1 Quy ước chung
- Đơn vị: 1 unit = 1 m. +Y lên, mặt trước = -Z, +X = phải.
- Origin: chân vật thể chạm y=0, tâm theo X/Z (xe: origin giữa trục, y=0 mặt đất).
- Chỉ dùng primitive three: `BoxGeometry`, `CylinderGeometry`, `SphereGeometry`, `CapsuleGeometry`, `TorusGeometry`, `ConeGeometry`, `ExtrudeGeometry`/`LatheGeometry` khi cần.
- Material: `MeshStandardMaterial` (flatShading: true cho low-poly). Emissive chỉ cho pickup/đèn.
- Bảng màu (hex):
  - player `#3B82F6`, player-accent `#F8FAFC`
  - enemy-chaser `#EF4444`, enemy-shooter `#A855F7`, enemy-tank `#78350F`, boss `#111827` + accent `#F59E0B`
  - coin `#FACC15`, shield `#22D3EE`, magnet `#F43F5E`, health `#22C55E`
  - ground `#374151`, lane-line `#E5E7EB`, obstacle `#F97316`
- Mỗi vật thể: `Group` đặt `name` theo tên bảng; mesh con đặt `name` rõ ràng (`body`, `wheel_fl`, `head`...) để animation/test truy cập.
- Bóng: `castShadow = true` cho mesh chính; ground `receiveShadow = true`.
- Collider: hộp AABB (hoặc sphere nếu ghi) lưu tại `group.userData.collider = { type, size:[x,y,z], offset:[x,y,z] }`.
- Poly budget: nhân vật <= 800 tri, xe <= 1500 tri, prop <= 300 tri, pickup <= 200 tri.
- Mỗi hàm tạo trả về vật thể + `dispose()` giải phóng geometry/material. Geometry/material dùng chung (cache theo tên) khi spawn nhiều bản (instancing cho coin, đạn).

### 12.2 Runner
| Vật thể | Hình dạng | Kích thước | Màu/Material | Collider | Animation |
|---|---|---|---|---|---|
| `runner_player` | Thân: `CapsuleGeometry(0.3, 0.7)`. Đầu: sphere r=0.25 đặt y=1.35. Mũ/kính: box 0.5x0.12x0.3 phía trước đầu. 2 tay + 2 chân: box 0.12x0.5x0.12 gắn pivot tại vai/hông (để xoay) | cao ~1.7, rộng 0.7 | thân `#3B82F6`, kính/mũ `#F8FAFC`, rough 0.6 | box 0.6x1.6x0.5, offset y=0.8 | chạy: tay/chân xoay đối pha ±45° @ 8Hz; nhảy: chân co 60°; lướt: scaleY 0.5 + nghiêng ngửa 70° |
| `coin` | `CylinderGeometry(0.25, 0.25, 0.06, 16)` xoay nằm đứng (trục Z) | đường kính 0.5 | `#FACC15`, metalness 0.8, rough 0.3, emissive nhẹ `#A16207` | sphere r=0.35 | xoay quanh Y 2 rad/s, bob ±0.1 |
| `shield_pickup` | Sphere r=0.35 lưới (wireframe) + `ConeGeometry` đảo ngược làm khiên bên trong | r 0.35 | `#22D3EE`, opacity 0.5, emissive | sphere r=0.45 | pulse scale 0.95-1.05 |
| `magnet_pickup` | `TorusGeometry(0.25, 0.08, 8, 16, Math.PI)` hình chữ U + 2 hộp đầu cực trắng | cao 0.5 | thân `#F43F5E`, đầu cực `#F8FAFC` | sphere r=0.45 | xoay Y 1.5 rad/s |
| `obstacle_low` | Hộp | 1.4 x 0.6 x 0.6 | `#F97316` + sọc vàng đen (texture canvas hoặc 3 box mỏng) | box khớp | không |
| `obstacle_high` | 2 cột box 0.2x2.2x0.2 + thanh ngang 1.4x0.3x0.2 ở y=1.2..1.5 (lướt qua dưới) | 1.4 x 2.2 x 0.3 | `#F97316` | thanh ngang box riêng | không |
| `obstacle_pit` | Mặt đất khoét lỗ 1.4 x 3.0; đáy `#0F172A` thấp 1.5 | 1.4 x 3.0 | ground + đáy tối | trigger box | không |
| `runner_chunk` | Sàn box 4.5 (3 lane x 1.5) x 0.4 x 20 dài; 2 vạch lane `#E5E7EB` mỏng 0.05; rào bên 2 cạnh cao 0.4 | 4.5 x 0.4 x 20 | `#374151` rough 0.9 | sàn box | không |

### 12.3 Shooter
| Vật thể | Hình dạng | Kích thước | Màu | Collider | Animation |
|---|---|---|---|---|---|
| `shooter_player` | Thân box 0.6x0.9x0.4, đầu box 0.4³ có visor, 2 tay box, súng gắn tay phải (xem 12.3 vũ khí), ba lô box 0.4x0.5x0.2 | cao 1.8 | `#3B82F6` + `#F8FAFC` | capsule r=0.35 h=1.7 | đi: chân/tay đối pha; bắn: giật súng lùi 0.1 trong 80 ms |
| `enemy_chaser` | Thân sphere r=0.4 méo (scale 1,1.2,1), 2 mắt sphere r=0.07 trắng, 2 càng cone hướng trước | cao 1.0 | `#EF4444` | sphere r=0.45 | nhún Y ±0.08 @ 6Hz, nghiêng về phía player |
| `enemy_shooter` | Thân cylinder r=0.35 h=1.1, đầu sphere r=0.25, nòng súng cylinder r=0.06 dài 0.6 tay phải | cao 1.5 | `#A855F7` | capsule r=0.35 h=1.4 | bắn: nòng giật; chết: scale→0 trong 200 ms |
| `enemy_tank` | Thân box 1.4x1.0x1.8, tháp pháo cylinder r=0.4 h=0.3 + nòng cylinder r=0.1 dài 1.0, 2 dải xích box 0.3x0.5x1.9 hai bên | 1.4 x 1.4 x 1.9 | `#78350F`, xích `#1F2937` | box khớp | tháp xoay theo player |
| `boss` | Như tank x2 scale + 4 cột gai cone quanh thân + lõi sphere phát sáng `#F59E0B` | 3 x 3 x 4 | `#111827`, lõi emissive | box khớp | lõi pulse; mở lõi khi cho phép sát thương |
| `bullet` | Sphere r=0.06 (player), r=0.1 (enemy) | — | player `#FACC15`, enemy `#F87171`, emissive | sphere | bay thẳng, trail 4 frame (instanced) |
| `weapon_pistol` | Hộp thân 0.08x0.14x0.3 + nòng cylinder r=0.02 dài 0.15 | dài 0.3 | `#374151` | — | giật 0.05 |
| `weapon_shotgun` | 2 nòng cylinder r=0.025 dài 0.7 song song + báng box | dài 0.9 | gỗ `#92400E` + thép `#4B5563` | — | giật 0.12 |
| `weapon_smg` | Thân box 0.08x0.14x0.45 + ổ đạn box 0.05x0.2x0.08 + nòng cylinder dài 0.2 | dài 0.6 | `#1F2937` | — | rung nhẹ liên tục khi bắn |
| `pickup_health` | Dấu cộng 3D: 2 box 0.4x0.12x0.12 vuông góc, trong khung hộp trắng | 0.4 | `#22C55E` | sphere r=0.4 | bob + xoay |
| `pickup_weapon` | Mô hình vũ khí tương ứng thu nhỏ 0.7x trên bệ cylinder r=0.3 h=0.1 | — | màu vũ khí + vòng sáng | sphere r=0.5 | xoay Y |
| `shooter_arena` | Sàn tròn/vuông 30x30, tường box cao 2 bao quanh, 6-8 cột/thùng box rải làm cover (1x1.2x1 đến 2x1.2x1) | 30 x 30 | sàn `#374151`, cover `#6B7280` | box từng cover | không |

### 12.4 Racing
| Vật thể | Hình dạng | Kích thước | Màu | Collider | Animation |
|---|---|---|---|---|---|
| `car_player` | Thân box 1.8x0.5x4.0 (thấp), cabin box 1.5x0.45x1.8 đặt y=0.5 lùi sau, kính trước nghiêng (box xoay -25°), 4 bánh `CylinderGeometry(0.35,0.35,0.3)` xoay trục Z, cánh gió sau box 1.6x0.05x0.4 + 2 trụ, 2 đèn trước box phát sáng | 1.8 x 1.0 x 4.0 | thân `#3B82F6`, cabin `#111827`, bánh `#1F2937`, đèn `#FEF3C7` emissive | box 1.8x0.9x4.0 | bánh quay theo vận tốc, bánh trước lái ±30°, thân nghiêng ±4° khi vào cua, đèn phanh đỏ khi S |
| `car_ai_1..3` | Như `car_player`, đổi màu `#EF4444` / `#22C55E` / `#F59E0B` | như trên | — | như trên | như trên |
| `track_straight` | Mặt đường box 12 x 0.2 x 20 + 2 gờ (kerb) sọc đỏ trắng 0.4 rộng + vạch giữa đứt | 12 x 0.2 x 20 | `#374151`, kerb `#EF4444`/`#F8FAFC` | sàn | không |
| `track_curve` | `RingGeometry` hoặc đường extrude theo cung 90°, bán kính trong 20, rộng 12 | 90° | như trên | sàn | không |
| `checkpoint_gate` | 2 trụ cylinder r=0.2 h=5 + thanh ngang box 12x0.4x0.4; start/finish có caro trắng đen | 12 x 5 | trụ `#F8FAFC`, thanh `#F59E0B` | trigger box 12x5x1 | cờ vẫy (vertex shader sin) |
| `prop_cone` | Cone r=0.2 h=0.6 + đế box 0.5x0.05x0.5 | 0.5 x 0.6 | `#F97316` + sọc trắng | sphere r=0.3, bị đẩy | đổ khi va chạm |
| `prop_tree` | Thân cylinder r=0.15 h=1.2 + 2 cone tán lá chồng (r=1.0 h=1.5; r=0.7 h=1.2) | cao 3.5 | thân `#78350F`, lá `#166534` | cylinder r=0.3 (không xuyên) | không |
| `prop_barrier` | Hàng rào hộp 3x0.8x0.3 sọc đỏ trắng, đặt ngoài kerb | 3 x 0.8 x 0.3 | `#EF4444`/`#F8FAFC` | box khớp | không |

### 12.5 Môi trường chung
- Skybox: gradient 2 màu (`#60A5FA` đỉnh → `#E0F2FE` chân trời) bằng `ShaderMaterial` hoặc `scene.background` canvas texture.
- Ánh sáng: `DirectionalLight` (cường độ 2.5, góc 45°, bóng 2048) + `HemisphereLight` (0.6).
- Sương: `Fog('#E0F2FE', 40, 120)` che pop-in chunk.

### 12.6 Checklist test model (pass/fail mỗi vật thể)
- [ ] Hàm `createX()` chạy không lỗi, trả `Group` đúng `name`.
- [ ] Kích thước bounding box nằm trong sai số 10% so với bảng.
- [ ] Origin đúng quy ước (chân y=0).
- [ ] Màu hex và material đúng bảng.
- [ ] Mesh con đặt tên đủ cho animation.
- [ ] `userData.collider` có và khớp kích thước.
- [ ] Tri count nằm trong budget (`renderer.info.render.triangles`).
- [ ] `dispose()` không leak (`renderer.info.memory` về mức cũ).
- [ ] Ngoại hình nhận diện được ngay ở góc camera game (ảnh chụp review).
- Cách chấm: trang `/dev/gallery` hiển thị mọi vật thể xoay 360° + bảng số liệu bbox/tri count. Người review so sánh với bảng trên.
