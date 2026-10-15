# Phân Tích Kiến Trúc & Kế Hoạch Chuyển Đổi Harness UI sang Astro + GitHub Actions + Jenkins CI/CD

- **Mục tiêu**: Tách giao diện **Harness UI (Paseo Control Center)** từ chuỗi HTML nhúng trong [harness_dashboard.py](file:///home/baoltb/Desktop/Paseo_Project/scripts/harness_dashboard.py) sang dự án **Astro (`https://astro.build/`)** đặt trực tiếp ở **ngoài thư mục `projects/`** (tại `/home/baoltb/Desktop/Paseo_Project/harness-ui/`) để được **Git theo dõi (tracked)**, đẩy thẳng lên repo `Room_Agent.git`, và tự động kiểm thử/triển khai qua **GitHub Actions (`.github/workflows/ci.yml`)** kết hợp **Jenkins (`Jenkinsfile`)**.
- **Trạng thái hiện tại**:
  - `scripts/harness_dashboard.py` (1.945 dòng code) đang gộp chung cả `ThreadingHTTPServer` (cổng `8765`) lẫn ~1.500 dòng HTML/CSS/Vanilla JS trong biến chuỗi `HTML_TEMPLATE`.
  - Trong [.gitignore](file:///home/baoltb/Desktop/Paseo_Project/.gitignore#L79-L80), thư mục `/projects/` đang bị ignore (`# 7. Sub-projects (own repos)`). Do đó, **tuyệt đối không đặt Astro UI trong `projects/`** mà phải đặt ở cấp root `/home/baoltb/Desktop/Paseo_Project/harness-ui/` (hoặc repo độc lập ngoài `projects/`) để đẩy lên Git và chạy GitHub Actions + Jenkins.

---

## 1. Tại Sao Đặt `harness-ui/` Ở Ngoài `projects/`?

| Vị trí đặt Astro UI | Trạng thái Git (`.gitignore`) | Chạy được GitHub Actions (`.github/workflows/`)? | Chạy được Jenkins (`Jenkinsfile`) từ Git? | Đánh giá |
| :--- | :--- | :--- | :--- | :--- |
| ❌ `projects/harness-ui/` | Bị chặn bởi dòng `80: /projects/` trong [.gitignore](file:///home/baoltb/Desktop/Paseo_Project/.gitignore#L80) | ❌ Không (code không lên Git) | ❌ Không (Jenkins clone repo sẽ thiếu thư mục này) | **Loại bỏ** |
| ✅ **`harness-ui/` (Ngay tại Root dự án)** | **Được Git track 100%** (chỉ ignore `node_modules/`, `dist/`, `.astro/`) | ✅ **Chạy trực tiếp trên `.github/workflows/ci.yml`** mỗi khi `git push` / tạo PR | ✅ **Jenkins pull 1 repo duy nhất** có đủ cả Python Backend (`tools/`, `scripts/`) + Astro Frontend (`harness-ui/`) | **Khuyên dùng (Tối ưu nhất)** |
| 🔹 `/home/baoltb/Desktop/harness-ui/` (Repo Git riêng hoàn toàn) | Repo Git độc lập | ✅ Có `.github/workflows/ci.yml` riêng | ✅ Có `Jenkinsfile` riêng (nhưng cần cấu hình CORS/URL sang Backend repo) | Phù hợp nếu tách team FE/BE hoàn toàn |

---

## 2. Đánh Giá Kỹ Thuật: Tại Sao Chọn Astro Cho Harness UI?

1. **Kiến trúc Islands (`Astro Islands`) tối ưu hiệu năng**:
   - Khung giao diện (Topbar, Sidebar, KPI Summary, trang đọc tài liệu Spec `docs/spec/*.md`, trang đọc Sổ cái [AGENT_PROGRESS.md](file:///home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md)) được biên dịch thành HTML tĩnh **0 KB JavaScript**.
   - Chỉ các vùng tương tác thời gian thực mới nạp JS độc lập (`client:load` / `client:visible`):
     - `WorkItemsIsland`: Bảng 317+ Work Items, bộ lọc nhanh, Modal tạo/chuyển trạng thái (`New -> Accepted -> Active -> Resolved -> Closed`).
     - `SlpcAgentsIsland`: Bảng điều khiển 4 Role **`SLPC` (`Supervisor - Lead - Peer - QC`)**, nút Dispatch gọi Paseo (`tools/call_agent.py`) và trình xem nhanh Context Window (`.jsonl`).
     - `QcWorkbenchIsland`: Giao diện chạy **5-Stage ISTQB Generator** (`tools/qc_test_generator.py`), xem độ phủ (`CI-TPxxx`) và cửa sổ Terminal stream log realtime.
     - `ProgressLedgerIsland`: Đọc dữ liệu từ `tools/agent_progress.py` và các Context Threads của 4 Role SLPC.
2. **Content Collections đọc trực tiếp Markdown cùng Repo**:
   - Vì `harness-ui/` nằm ngay ở root `/home/baoltb/Desktop/Paseo_Project/harness-ui/` và cùng được đẩy lên Git với `docs/spec/*.md` và `docs/AGENT_PROGRESS.md`, **Astro Content Layer API** có thể đọc trực tiếp `../docs/spec/*.md` ngay trong lúc build trên GitHub Actions và Jenkins mà không cần copy file thủ công.
3. **2 Chế độ Build linh hoạt**:
   - **`output: 'static'` (Khuyên dùng)**: Build ra `harness-ui/dist/` siêu nhẹ (~3–5 giây trên GitHub Actions & Jenkins). Backend Python (`scripts/harness_dashboard.py --serve --port 8765`) hoặc Nginx phục vụ trực tiếp `harness-ui/dist/` và giữ nguyên các API `/api/*`.
   - **`output: 'server'` (`@astrojs/node`)**: Chạy Node SSR độc lập nếu muốn mở rộng thêm middleware xác thực (Auth) tại tầng Frontend.

---

## 3. Cấu Trúc Thư Mục Tại Root (Ngoài `projects/`, Đẩy Lên Git)

```text
/home/baoltb/Desktop/Paseo_Project/
├── .github/
│   └── workflows/
│       └── ci.yml                # GitHub Actions: Gitleaks + Python Harness Tests + Astro Check & Build
├── Jenkinsfile                   # Jenkins Declarative Pipeline tại root repo
├── harness-ui/                   # Dự án Astro nằm NGOÀI /projects/ -> được Git track đầy đủ
│   ├── astro.config.mjs          # Cấu hình Astro + Vite proxy /api -> http://127.0.0.1:8765
│   ├── package.json              # Astro 5.x, TypeScript
│   ├── package-lock.json         # Lockfile bắt buộc để GitHub Actions & Jenkins chạy `npm ci`
│   ├── tsconfig.json
│   ├── deploy/
│   │   ├── nginx-harness-ui.conf # Cấu hình Nginx phục vụ harness-ui/dist/ + proxy /api/*
│   │   └── Dockerfile            # Multi-stage build (node:22-alpine -> nginx:alpine)
│   └── src/
│       ├── layouts/
│       │   └── DashboardLayout.astro
│       ├── components/
│       │   ├── KpiStrip.astro
│       │   ├── WorkItemsBoard.astro
│       │   ├── SlpcAgentsPanel.astro
│       │   ├── QcWorkbench.astro
│       │   └── ProgressLedger.astro
│       ├── pages/
│       │   ├── index.astro       # Paseo Control Center (Work Items, SLPC Agents, QC Workbench, Progress)
│       │   └── specs/
│       │       └── [...slug].astro # Render trực tiếp ../docs/spec/*.md
│       └── styles/
│           └── global.css
├── scripts/
│   └── harness_dashboard.py      # Tự động ưu tiên phục vụ harness-ui/dist/ nếu đã build + giữ nguyên /api/*
└── tools/
    ├── test_harness.py
    └── test_qc_generator.py
```

### Cấu hình `harness-ui/astro.config.mjs`
```javascript
import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  server: {
    port: 4321,
    host: true,
  },
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8765',
          changeOrigin: true,
        },
      },
    },
  },
});
```

---

## 4. Thiết Kế GitHub Actions (`.github/workflows/ci.yml`)

Hiện tại [.github/workflows/ci.yml](file:///home/baoltb/Desktop/Paseo_Project/.github/workflows/ci.yml) mới chỉ có 2 job (`secrets` và `test` cho Python). Khi đặt `harness-ui/` ở ngoài `projects/`, ta mở rộng `.github/workflows/ci.yml` thêm job **`astro-ui`** (kiểm tra TypeScript `astro check`, build thử `npm run build`, và đóng gói Artifact `harness-ui-dist`):

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m compileall -q tools scripts
      - run: bash -n setup_harness.sh setup_home.sh
      - run: python tools/test_harness.py
        env:
          HARNESS_BACKEND: sqlite
          HARNESS_DB: ${{ runner.temp }}/harness_test.db
      - run: python tools/test_qc_generator.py

  astro-ui:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: harness-ui
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "npm"
          cache-dependency-path: harness-ui/package-lock.json
      - name: Install dependencies
        run: npm ci
      - name: Astro Type & Content Check
        run: npx astro check
      - name: Build Astro Static Bundle
        run: npm run build
      - name: Upload Production Bundle Artifact
        uses: actions/upload-artifact@v4
        with:
          name: harness-ui-dist
          path: harness-ui/dist/
          retention-days: 7
```

---

## 5. Thiết Kế Đường Ống Jenkins CI/CD (`Jenkinsfile` tại Root)

Đặt `Jenkinsfile` ngay tại `/home/baoltb/Desktop/Paseo_Project/Jenkinsfile`. Khi GitHub nhận code mới (đã vượt qua GitHub Actions hoặc qua GitHub Webhook bắn về Jenkins), Jenkins sẽ:
1. Chạy bộ test Python Harness (`test_harness.py` & `test_qc_generator.py`).
2. Chạy `npm ci`, `npx astro check`, `npm run build` bên trong `${WORKSPACE}/harness-ui`.
3. Đồng bộ `harness-ui/dist/` ra thư mục Web (`/var/www/harness-ui`) và khởi động lại daemon `scripts/harness_dashboard.py --daemon --port 8765`.
4. Ghi nhận kết quả build/deploy vào sổ cái `tools/agent_progress.py`.

```groovy
pipeline {
  agent any

  options {
    timestamps()
    timeout(time: 15, unit: 'MINUTES')
    disableConcurrentBuilds()
  }

  environment {
    APP_DIR      = "${WORKSPACE}/harness-ui"
    DEPLOY_ROOT  = "/var/www/harness-ui"
    API_PORT     = "8765"
    NODE_ENV     = "production"
  }

  stages {
    stage('1. Verify Backend Python Harness & QC Generator') {
      steps {
        sh '''
          python3 --version
          python3 -m compileall -q tools scripts
          python3 tools/test_harness.py
          python3 tools/test_qc_generator.py
        '''
      }
    }

    stage('2. Install Astro UI Dependencies') {
      steps {
        dir("${env.APP_DIR}") {
          sh '''
            node -v
            npm -v
            npm ci --prefer-offline --no-audit
          '''
        }
      }
    }

    stage('3. Astro Check & Build Static Bundle') {
      steps {
        dir("${env.APP_DIR}") {
          sh '''
            npx astro check
            npm run build
          '''
        }
      }
    }

    stage('4. Deploy Static Bundle & Ensure Harness API Daemon') {
      steps {
        sh '''
          # Khởi động/reload Backend API Server ở cổng 8765
          python3 scripts/harness_dashboard.py --daemon --port ${API_PORT}

          # Nếu server có thư mục DEPLOY_ROOT cho Nginx thì đồng bộ sang
          if [ -w "$(dirname ${DEPLOY_ROOT})" ] || [ -w "${DEPLOY_ROOT}" ]; then
            mkdir -p ${DEPLOY_ROOT}
            rsync -av --delete ${APP_DIR}/dist/ ${DEPLOY_ROOT}/
          fi
        '''
      }
    }

    stage('5. Post-Deploy Smoke Test') {
      steps {
        sh '''
          curl -fsS http://127.0.0.1:${API_PORT}/api/agents > /dev/null
          test -f ${APP_DIR}/dist/index.html
        '''
      }
    }
  }

  post {
    always {
      sh '''
        python3 tools/agent_progress.py log \
          --agent "Jenkins CI/CD" \
          --summary "Build & Deploy Astro Harness UI (root harness-ui/)" \
          --done "Verified Python Harness, built harness-ui/dist, smoke-tested API :8765" \
          --files "harness-ui/dist/index.html" || true
      '''
    }
  }
}
```

---

## 6. Cơ Chế Tích Hợp Ngược Với `scripts/harness_dashboard.py`

Để đảm bảo vừa chạy mượt khi dev local (`:8765` hoặc `:4321`), vừa chạy mượt trên Jenkins/Nginx:
- Khi `GET /` hoặc các file tĩnh (`/_astro/*`, `/favicon.svg`) gửi vào `scripts/harness_dashboard.py`:
  - Nếu thư mục `/home/baoltb/Desktop/Paseo_Project/harness-ui/dist/index.html` đã tồn tại (do Astro build ra), `harness_dashboard.py` sẽ phục vụ trực tiếp các file tĩnh từ `harness-ui/dist/`.
  - Nếu chưa build `harness-ui/dist/`, `harness_dashboard.py` tự động fallback về `HTML_TEMPLATE` sẵn có (không bao giờ gây gián đoạn dịch vụ).
- Bổ sung thêm endpoint `GET /api/progress` trong `scripts/harness_dashboard.py` để Astro UI hiển thị trực tiếp Sổ cái tiến độ [AGENT_PROGRESS.md](file:///home/baoltb/Desktop/Paseo_Project/docs/AGENT_PROGRESS.md) và danh sách các phiên Context Window (`.jsonl`) của 4 Role **`SLPC` (`Supervisor - Lead - Peer - QC`)**.
