# Architecture Specification: RTK Pipelines, Methods & Compression Engine

> **Spec Identifier**: `ARCH-SPEC-RTK-PIPELINES-METHODS-2026-V1`  
> **Source Reference**: [https://www.rtk-ai.app/docs/pipelines/methods/](https://www.rtk-ai.app/docs/pipelines/methods/)  
> **Scope**: Comprehensive architecture, method taxonomy, pipeline grammar, condition engine, AI classifiers, and proxy-resident compression for Rust Token Killer (RTK v1.0).

---

## 1. Executive Summary & Dual-Layer Architecture

RTK (Rust Token Killer) optimizes LLM coding agent token consumption by operating at two distinct interception layers:
1. **Hook Layer (`hook`)**: Operates inside the coding agent around tool calls.
   - **`before_tool`**: Intercepts before execution. Can rewrite shell commands (`rtk <cmd>`), deny execution with explanations, or route tasks to lightweight/cheaper models.
   - **`after_tool`**: Compresses raw command stdout/stderr or tool output before the agent context absorbs it. Full raw logs remain recoverable via `rtk recall <hash>`.
2. **Proxy Layer (`proxy`)**: A local HTTP daemon (`rtk-proxy`) situated between the coding agent and the LLM provider API.
   - Intercepts requests, strips redundant redraws/ANSI/duplicates, aligns prompt-cache breakpoints (`cache-align`), and compresses historical tool results via **CCR (Compressed Context Retrieval)** without breaking prompt caching.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       RTK DUAL-LAYER INTERCEPTION PIPELINE                   │
│                                                                             │
│  [AGENT TOOL EXECUTION]                                                     │
│       │                                                                     │
│       ├──► (Hook) before_tool : Rewrite CLI / Route to Task / Deny           │
│       ├──► (Tool Execution)   : Real bash / search / read runs              │
│       └──► (Hook) after_tool  : Compress Output via Method Chains (Lossy/   │
│                                 Lossless) ➔ Raw saved to Recall Store       │
│                                                                             │
│  [AGENT HTTP REQUEST TO MODEL]                                              │
│       │                                                                     │
│       ▼                                                                     │
│  [RTK LOCAL PROXY DAEMON (:8080)]                                           │
│       ├──► Normalization   : ansi, progress, dedup (byte-stable)            │
│       ├──► Cache Alignment : cache-align breakpoint placement               │
│       ├──► CCR Retrieval   : In-conversation compression with rtk_retrieve  │
│       └──► Forward to Upstream API (Anthropic / OpenAI / Google)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Exhaustive Methods Taxonomy

A **Method** is a discrete text transform block. Rules chain methods via `use = ["..."]`. Chains are statically checked at load time to prevent invalid inputs. Terminal methods (`toon`) are strictly validated to run last.

### 2.1 Built-in Methods (Hook + Proxy Sites)

| Method | Type | Recovery Mechanism | Execution Context | Functional Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `ansi` | Lossless | None (pure cleanup) | `tool_result` (normalize) | Strips ANSI escape sequences and terminal formatting codes. |
| `progress` | Lossy | `rtk recall` (hook site) | `tool_result` (normalize) | Keeps only the final state/frame of animated `\r` progress bars. |
| `dedup` | Lossless | None | `tool_result` (normalize) | Collapses $\ge 3$ consecutive identical adjacent lines into `[xN]`. |
| `base64-elide` | Lossy | None (value-free blobs) | `tool_result` | Detects long base64 string runs and replaces them with size annotations. |
| `cap` | Lossy | `rtk recall <hash>` | `hook.after_tool` (requires recall) | Structural line cap: if output exceeds 300 lines, retains head 50 + tail 200 lines and saves the full original to disk. |
| `toon` | Lossy (Terminal) | `rtk recall` (hook site) | `hook.after_tool` (requires recall) | Converts uniform arrays of flat objects into TOON format; falls back to minified JSON. |
| `minify-json` | Lossy | `rtk recall` (hook site) | `hook.after_tool` (requires recall) | Compresses JSON by stripping whitespace and non-essential formatting. |
| `web-md` | Lossless | None | `tool_result` | Converts raw HTML content into structured Markdown. |
| `md-slim` | Lossy | None (read-noise) | `tool_result` | Trims Markdown noise: removes status badges, HTML comments, and blank line runs while preserving URLs and code blocks. |
| `grep-group` | Lossy | `rtk recall` (hook site) | `hook.after_tool` (requires recall) | Groups `path:line:content` matches by file name; preserves every match without omitting locations. |
| `lockfile` | Lossy | None | `tool_result` | Compresses massive dependency lockfiles (`package-lock.json`, `Cargo.lock`) into a concise `name@version` list. |
| `strip-line-numbers` | Lossy | None (default: off) | `tool_result` (normalize) | Strips line-number prefixes from file reading outputs for agents that do not address lines numerically. |
| `truncate` | Lossy | `rtk recall` | `hook.after_tool` (requires recall) | Hard structural line truncation. |
| `shape` | Lossy | `rtk recall` | `hook.after_tool` (requires recall) | Normalizes output, classifies layout shape, and renders per-shape summary. |
| `rle` | Lossy | `rtk recall` (hook site) | `hook.after_tool` (requires recall) | Run-length encoding collapse of adjacent identical lines. |

*Note on Recovery Requirement*: Methods marked "needs recall" are skipped under `proxy.request` because the proxy daemon does not persist recall copies during forwarding.

### 2.2 Proxy-Resident Methods

Implemented exclusively in the RTK Proxy daemon:

| Method | Type | Recovery Mechanism | Execution Target | Functional Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `cache-align` | Lossless | None | `proxy.request.cache` | Automatically positions prompt cache breakpoints; no-op if client sets its own. |
| `ccr` | Lossy | `rtk_retrieve` tool call | `proxy.request.tool_result` | Compresses large tool results already in conversation history to a preview + marker; injects dynamic retrieval tool. |
| `retire-pointer` | Lossy | Disk file + `rtk_retrieve` | `proxy.request.tool_use` | Replaces echoed file bodies in write/edit requests with a pointer to disk. |

---

## 3. Shipped Composites (Chains) & Custom Chains

RTK groups atomic methods into pre-validated composite chains usable in any rule:

### 3.1 Pre-shipped Chains
- **`term`**: `["ansi", "progress", "dedup", "base64-elide", "cap"]` — Default CLI output compression.
- **`json`**: `["base64-elide", "toon"]` — Minification and tabular restructuring of JSON data.
- **`web`**: `["ansi", "base64-elide", "web-md", "toon", "md-slim"]` — HTML-to-clean-Markdown conversion.
- **`matches`**: `["grep-group"]` — Grep search results formatting.

### 3.2 Defining Custom Chains
Custom chains can be authored in `pipeline.toml` by declaring composite methods:

```toml
[method.gentle]
chain = ["ansi", "dedup"]

[[hook.after_tool.shell]]
name = "gentle-term"
use = ["gentle"]
```

---

## 4. Pipeline Configuration Specification (`pipeline.toml`)

### 4.1 File Hierarchy & Discovery Order

| Level | Path | Scope | Semantics |
| :--- | :--- | :--- | :--- |
| **Built-in** | `rtk:default`, `rtk:posthook`, `rtk:proxy`, `rtk:delegate-reads`, `rtk:terse` | Core | Compiled directly into the binary. |
| **User** | `~/.config/rtk/pipeline.toml`<br>`~/.config/rtk/pipelines/*.toml` | Global | Evaluated first across all projects. |
| **Project** | `.rtk/pipeline.toml`<br>`.rtk/pipelines/*.toml` | Project | Trust-gated (`rtk init` prompts user). Overrides user rules. |

*Precedence*: Built-ins ➔ User pipeline ➔ User pipelines directory ➔ Project pipeline ➔ Project pipelines directory (Later wins).

### 4.2 Top-Level Grammar Schema

```toml
schema_version = 1

[pipeline]
name = "custom-room-pipeline"
extends = ["rtk:default", "rtk:proxy"]
enabled = true

[[hook.before_tool.shell]]
name   = "rtk-rewrite"
action = "rewrite"

[[hook.after_tool.shell]]
name   = "term-default"
when   = { is_rtk_command = false }
use    = ["term"]

[[directive]]
use = "terse-output"

[guards]
never_worse = true
min_size = 512
```

### 4.3 Subjects & Interception Tree

A rule is uniquely identified by its hierarchy position: `[[<site>.<event>.<subject>]]`:
- **Sites**: `hook`, `proxy`.
- **Events**: `before_tool`, `after_tool`, `request`.
- **Hook Subjects**:
  - `shell`: Shell execution (`Bash`, `PowerShell`, `terminal`).
  - `read`: File reading (`Read`, `NotebookRead`).
  - `write`: File authoring (`Write`).
  - `edit`: File patching (`Edit`, `MultiEdit`).
  - `search`: Search utilities (`Grep`, `Glob`, `search_files`).
  - `web`: Web fetching (`WebFetch`, `WebSearch`).
  - `subagent`: Sub-agent delegations (`Task`, `Agent`, `delegate_task`).
  - `mcp`: External MCP servers (`mcp__*`).
  - `any`: Universal fallback.

---

## 5. Control Actions & Delegation Routing

Before or after tools execute, rules can trigger control actions instead of simple transform chains:

| Action | Allowed Positions | Behavior |
| :--- | :--- | :--- |
| **`rewrite`** | `hook.before_tool.shell` | Intercepts CLI and rewrites to `rtk <cmd>` if a filter exists; otherwise passes untouched. |
| **`deny`** | `hook.before_tool.*` | Refuses execution; shows interpolated error message (`${command}`, `${file_path}`). |
| **`passthrough`** | All hook positions | Bypasses processing; exempts command from rewrites or compression. |
| **`route`** | `before_tool`, `after_tool` | Hands work over to a background task running an upstream model. |

### 5.1 Route Modes Before Tool Calls
- **`suggest`** (Default): Denies the original call and provides the agent with an exact CLI task invocation command.
- **`swap`**: Silently replaces the command with the delegated task while preserving process exit codes.
- **`answer`**: Blocks the hook briefly to fetch the answer from a fast upstream model (`timeout_secs` bounded).

---

## 6. Conditions Engine & AI Classifiers (Judges)

### 6.1 Deterministic Operators (`when`)
- **Equality**: `format = "json"`, `whole_file = true`.
- **Membership**: `basename_in = ["package-lock.json", "Cargo.lock"]`.
- **String matching**: `command_starts_with = "git "`, `command_matches = "^npm (test|run)"`.
- **Numeric comparison**: `tokens_gt = 1500`, `file_lines_gte = 400`, `duration_ms_gt = 5000`.

### 6.2 Call Context Awareness
Rules inspect agent intent directly:
- `intent`: Last ~600 characters of agent reasoning or explanation.
- `goal`: User prompt text (first ~600 characters).
- `recent_calls`: Recent 5 tool calls formatted as pipe-separated items.

### 6.3 AI Classifiers (`[classifier.*]`)
Classifiers query fast upstream endpoints (e.g., Kev System One / Flash models) to extract semantic facts:
- `choice`: Categorical classification (`labels` map).
- `score`: Continuous scoring (0.0 to 1.0 against a defined `rubric`).
- `noul`: Binary truth probability (0.0 to 1.0).

```toml
[upstream.kev]
provider     = "typesafe"
model        = "systemone-fast"
base_url     = "http://127.0.0.1:8008/v1/systemone"
timeout_secs = 2

[classifier.code_intent]
upstream       = "kev"
question       = "choice"
instructions   = "Classify whether tool output indicates a regression failure or normal log."
input_chars    = 1500
min_confidence = 0.85

[classifier.code_intent.labels]
test_failure   = "Assertions failed, stacktrace, panic, or exit code non-zero"
normal_compile = "Successful compilation, build metrics, info progress"
```

---

## 7. Tasks & Upstreams Specification

Tasks allow agents to delegate heavy reading or synthesis to cost-effective worker models:

### 7.1 Built-in Task Kinds
1. **`summarize`**: Ingests files + agent question ➔ Outputs structured bullet summary (`rtk <task> --question "..." <files>`).
2. **`digest`**: Captures raw output + question ➔ Outputs distilled takeaways (`rtk <task> --question "..." -- <cmd>`).
3. **`generate`**: Ingests specification + reference implementation ➔ Synthesizes target file directly on disk (`rtk <task> --spec "..." --reference <ref> --target <out>`).

```toml
[upstream.gemini_flash]
provider     = "google"
model        = "gemini-3.8-flash-high"
api_key_env  = "GEMINI_API_KEY"
timeout_secs = 20

[task.bulk-read]
kind        = "summarize"
upstream    = "gemini_flash"
temperature = 0.1
context     = true
```

---

## 8. Compressed Context Retrieval (CCR) in Proxy

Under `proxy.request.tool_result`, RTK Proxy activates **CCR (Compressed Context Retrieval)**:
1. When tool results in conversation history exceed `tokens_gt = 1500`, the block is replaced by a preview marker:
   `[rtk-proxy: compressed 4200 tokens — call rtk_retrieve("0c81bf9a") to get the full content]`
2. An ephemeral tool definition `rtk_retrieve` is automatically exposed to the LLM.
3. If the LLM requests the original text, the proxy intercepts the request and responds locally from SQLite store `~/.config/rtk/llm-proxy/rtk-proxy-memory.db` without passing the round-trip to the remote provider.
4. Preserves prompt caching across turns since the marker string is byte-stable.

---

## 9. Rust Plugin SDK (`rtk-plugin`)

For proprietary transforms, developers create native Rust crates compiled directly into the binary:

### 9.1 Scaffolding and Build
```bash
rtk plugins new my_transform
# Implement Method trait in my_transform/src/lib.rs
rtk plugins build
```

### 9.2 Rust Method Trait Implementation
```rust
use rtk_plugin::{rtk_plugin, Block, Method, MethodCtx, MethodInfo, Outcome};

struct ScrubInternalTokens;

impl Method for ScrubInternalTokens {
    fn name(&self) -> &'static str {
        "scrub-tokens"
    }

    fn info(&self) -> MethodInfo {
        MethodInfo::LOSSLESS_TRANSFORM
    }

    fn apply(&self, block: &Block, _ctx: &MethodCtx) -> Outcome {
        let cleaned = block.text.replace("INTERNAL_SECRET_", "REDACTED_");
        Outcome::Continue(cleaned)
    }
}

rtk_plugin!(ScrubInternalTokens);
```

---

## 10. SLPPC Room Integration Blueprint (`Room_Agent`)

To maximize token conservation across `Room_Agent` while protecting role invariants:
1. **Supervisor & PM Profile**: Bound to `rtk:terse` and `rtk:proxy` with `cache-align` to eliminate conversational verbosity.
2. **Lead Profile**: Configured with `rtk:verbatim-diffs` to ensure Git diffs and code contracts reach the architect with 100% byte fidelity.
3. **Peer Sub-Agents**: Bound to `rtk:posthook` with `term` and `matches` chains, saving 60–90% token output during local test runner execution (`jest`, `nx test`, `cargo test`).
4. **Mechanical Verification**: Ensure all recovery hashes and recall paths (`rtk recall`) remain active in local development storage.
