# Harness2 Rust Port Specification (Harness2-RS)

**Tài liệu**: Đặc tả Kỹ thuật Chuyển ngữ Framework Google Harness² sang Rust  
**Phiên bản**: 1.0.0  
**Tác giả**: Supervisor & SLPC Architecture Team  
**Mục tiêu**: Thiết kế kiến trúc, hệ thống kiểu dữ liệu và mô hình đồng thời hiệu năng cao cho việc port toàn bộ framework `projects/harness2` sang Rust.

---

## 1. Mục Tiêu & Lợi Thế Kỹ Thuật (Why Rust?)

Framework gốc `harness2` (Google Research, arXiv: 2610.14224) điều phối khối lượng tính toán lớn: $4k$ agent rollouts, $3k$ improvement stages, hàng trăm tiến trình CLI chạy song song. Việc chuyển đổi từ Python sang Rust đem lại:

1. **Zero Data-Race Concurrency**: Loại bỏ hoàn toàn Python GIL. Điều phối đồng thời hàng nghìn tác vụ rollout và streaming trajectory mà không bị bottleneck CPU.
2. **Deterministic Memory Footprint**: Python tiêu tốn ~50-80MB RAM cho mỗi process con nạp ast/inspect. Rust binary chỉ tốn <5MB base RSS, tối ưu hóa triệt để khi chạy sweep lớn.
3. **Compile-Time Budget Safety**: Sử dụng hệ thống kiểu dữ liệu chặt chẽ (Typestate pattern) để xác minh công thức ngân sách $R = 4k, P = 3k$ ngay trong quá trình biên dịch, triệt tiêu lỗi `BudgetError` lúc runtime.
4. **Resilient Subprocess Sandbox**: Quản lý vòng đời tiến trình con qua RAII `ChildGuard` (tự động gửi `SIGKILL` khi drop), triệt tiêu hoàn toàn orphan processes khi timeout hoặc bị cancel.

---

## 2. Cấu Trúc Workspace Cargo (`harness2-rs`)

Hệ thống được tổ chức theo mô hình multi-crate workspace:

```text
projects/harness2-rs/
├── Cargo.toml                  # Workspace manifest
├── crates/
│   ├── harness2-core/          # Pure Domain Logic & Algorithms
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── recursion.rs    # Dual-mode FSM (Parallel vs Sequential)
│   │   │   ├── ledger.rs       # Budget identity & session tracker
│   │   │   ├── tree.rs         # File tree manipulation & surface specs
│   │   │   ├── proposer.rs     # LLM Proposer client & prompt templates
│   │   │   ├── library.rs      # Cross-domain experience store
│   │   │   └── judge.rs        # Automated scoring & rubric evaluators
│   ├── harness2-substrate/     # Process Sandboxing & Agent Bridges
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── trait.rs        # Async Substrate trait definition
│   │   │   ├── codex.rs        # OpenAI Codex CLI wrapper & stream parser
│   │   │   ├── opencode.rs     # OpenCode CLI runner & Jinja sanitizer
│   │   │   └── sandbox.rs      # Environment isolation & child guard
│   ├── harness2-benchmarks/    # Benchmark Adapters
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── jobbench.rs     # JobBench evaluation adapter
│   │   │   ├── workbuddy.rs    # WorkBuddy evaluation adapter
│   │   │   └── lab.rs          # Lab research evaluation adapter
│   └── harness2-cli/           # Binary CLI
│       ├── src/
│       │   ├── main.rs         # CLI entry point (clap v4)
│       │   ├── sweep.rs        # Batch sweep coordinator
│       │   └── report.rs       # Output visualizer & metrics reporter
```

---

## 3. Hệ Thống Kiểu Dữ Liệu & Core Data Structures

### 3.1. Budget Ledger & Session Identity (`harness2-core/src/ledger.rs`)

Thay thế dictionary động của Python bằng các kiểu dữ liệu bất biến và thread-safe:

```rust
use std::collections::HashSet;
use std::sync::Arc;
use tokio::sync::RwLock;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum BudgetError {
    #[error("Exceeded rollout budget: requested {actual}, allowed {budget}")]
    RolloutExceeded { actual: usize, budget: usize },
    #[error("Exceeded session budget: requested {actual}, allowed {budget}")]
    SessionExceeded { actual: usize, budget: usize },
    #[error("Duplicate label detected: '{0}'")]
    DuplicateLabel(String),
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum StageKind {
    SharedBase,
    Invariant,
    Domain,
    Aggregate,
    Compose,
}

#[derive(Debug, Clone)]
pub struct LedgerEntry {
    pub label: String,
    pub kind: StageKind,
    pub attempts: usize,
    pub cost_usd: f64,
    pub cached: bool,
}

pub struct Ledger {
    k: usize,
    rollout_budget: usize,
    session_budget: usize,
    entries: RwLock<Vec<LedgerEntry>>,
    seen_labels: RwLock<HashSet<String>>,
}

impl Ledger {
    pub fn new(k: usize) -> Self {
        Self {
            k,
            rollout_budget: 4 * k,
            session_budget: 3 * k,
            entries: RwLock::new(Vec::with_capacity(3 * k)),
            seen_labels: RwLock::new(HashSet::new()),
        }
    }

    pub async fn record_session(&self, entry: LedgerEntry) -> Result<(), BudgetError> {
        let mut labels = self.seen_labels.write().await;
        if !labels.insert(entry.label.clone()) {
            return Err(BudgetError::DuplicateLabel(entry.label));
        }

        let mut entries = self.entries.write().await;
        if entries.len() >= self.session_budget {
            return Err(BudgetError::SessionExceeded {
                actual: entries.len() + 1,
                budget: self.session_budget,
            });
        }

        entries.push(entry);
        Ok(())
    }
}
```

---

### 3.2. Substrate Trait & Subprocess Isolation (`harness2-substrate/src/trait.rs`)

```rust
use async_trait::async_trait;
use std::path::{Path, PathBuf};
use tokio::io::AsyncRead;

#[derive(Debug, Clone)]
pub struct RunRequest {
    pub task_id: String,
    pub workspace_dir: PathBuf,
    pub timeout_secs: u64,
    pub env_vars: Vec<(String, String)>,
}

#[derive(Debug)]
pub struct RunResult {
    pub exit_code: i32,
    pub trajectory: String,
    pub duration_secs: f64,
    pub token_usage: Option<TokenUsage>,
}

#[async_trait]
pub trait Substrate: Send + Sync {
    /// Định danh engine (ví dụ: "cx" cho Codex, "oc" cho OpenCode)
    fn id(&self) -> &'static str;

    /// Kiểm tra môi trường (CLI đã cài đặt, API key sẵn sàng)
    async fn preflight(&self) -> Result<(), SubstrateError>;

    /// Chuẩn bị thư mục harness trong workspace
    async fn materialise(&self, target_dir: &Path, harness: &HarnessTree) -> Result<(), SubstrateError>;

    /// Thực thi agent task bên trong sandbox an toàn
    async fn execute(&self, request: RunRequest) -> Result<RunResult, SubstrateError>;
}
```

---

### 3.3. Dual-Mode Recursion Engine (`harness2-core/src/recursion.rs`)

Hiện thực hóa 2 chế độ đệ quy qua Async Tokio Tasks:

```rust
pub enum RecursionMode {
    Parallel,
    Sequential,
}

pub struct RecursionEngine<S: Substrate, B: BenchmarkAdapter> {
    substrate: Arc<S>,
    benchmark: Arc<B>,
    proposer: Arc<Proposer>,
    ledger: Arc<Ledger>,
    concurrency_limit: Arc<tokio::sync::Semaphore>,
}

impl<S: Substrate, B: BenchmarkAdapter> RecursionEngine<S, B> {
    pub async fn run(&self, mode: RecursionMode) -> Result<ModeResult, HarnessError> {
        match mode {
            RecursionMode::Parallel => self.run_parallel().await,
            RecursionMode::Sequential => self.run_sequential().await,
        }
    }

    async fn run_parallel(&self) -> Result<ModeResult, HarnessError> {
        // 1. Chạy k Shared Base Rollouts
        let base_results = self.execute_base_rollouts().await?;

        // 2. Chạy đồng thời 2k Improvement Stages (k Invariant + k Domain)
        let (inv_stages, dom_stages) = tokio::try_join!(
            self.spawn_stages(StageKind::Invariant, &base_results),
            self.spawn_stages(StageKind::Domain, &base_results)
        )?;

        // 3. Rollout 2k intermediate candidates
        let intermediate_evals = self.evaluate_candidates(&inv_stages, &dom_stages).await?;

        // 4. Lập lịch k Aggregation Stages (agg1..aggk)
        let final_harnesses = self.aggregate_finals(intermediate_evals).await?;

        Ok(ModeResult::new(final_harnesses))
    }

    async fn run_sequential(&self) -> Result<ModeResult, HarnessError> {
        let mut current_harness = self.get_base_harness().await?;
        let mut finals = Vec::with_capacity(self.ledger.k);

        // Chạy t = 1..k vòng tiến hóa nối tiếp
        for step in 1..=self.ledger.k {
            let inv = self.propose_stage(StageKind::Invariant, step, &current_harness).await?;
            let dom = self.propose_stage(StageKind::Domain, step, &current_harness).await?;

            // Compose hợp nhất kết quả vòng t làm nền tảng cho vòng t+1
            current_harness = self.compose_stages(step, inv, dom).await?;
            finals.push(current_harness.clone());
        }

        Ok(ModeResult::new(finals))
    }
}
```

---

## 4. Quản Lý Tiến Trình Con & Chống Rò Rỉ Tài Nguyên (RAII ChildGuard)

Khi chạy CLI agent (như Codex hoặc OpenCode), nếu timeout hoặc agent crash, Python dễ để lại tiến trình zombie. Rust giải quyết triệt để bằng `ChildGuard`:

```rust
pub struct ChildGuard {
    child: tokio::process::Child,
}

impl Drop for ChildGuard {
    fn drop(&mut self) {
        // Bắt buộc gửi SIGKILL nếu tiến trình chưa kết thúc khi bị drop
        let _ = self.child.start_kill();
    }
}
```

---

## 5. Kế Hoạch Dependencies (`Cargo.toml`)

Các thư viện chuẩn công nghiệp được chọn lọc kỹ càng, đảm bảo không thêm boilerplate:

```toml
[workspace]
members = [
    "crates/harness2-core",
    "crates/harness2-substrate",
    "crates/harness2-benchmarks",
    "crates/harness2-cli",
]
resolver = "2"

[workspace.dependencies]
tokio = { version = "1.40", features = ["full"] }
tokio-util = { version = "0.7", features = ["io"] }
async-trait = "0.1"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
reqwest = { version = "0.12", default-features = false, features = ["json", "rustls-tls"] }
thiserror = "1.0"
anyhow = "1.0"
clap = { version = "4.5", features = ["derive", "env"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
tempfile = "3.12"
walkdir = "2.5"
```

---

## 6. Tiêu Chuẩn Nghiệm Thu & Quality Gate (QC Verification)

1. **Strict Typing Standard**:
   - Biên dịch với `#![deny(clippy::all, clippy::pedantic)]`.
   - Cấm hoàn toàn `unwrap()`, `expect()` trong thư viện (bắt buộc dùng `Result` và `?`).
   - Cấm sử dụng `unsafe` trừ khi tương tác với syscall bắt buộc (được kiểm định riêng).
2. **Golden Master Test Suite**:
   - Thực thi file test đối chiếu: `tests/golden_master_parity.rs`.
   - Chạy cùng một seed và mock proposer, so sánh từng JSON state của `Ledger` giữa bản Python và Rust: sai số $0\%$.
3. **Budget Invariant Check**:
   - $100\%$ test suite phải khẳng định không có trường hợp nào rollout vượt $4k$ hay session vượt $3k$.
