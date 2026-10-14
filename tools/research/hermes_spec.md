# Hermes Agent Specification & Gateway Architecture

## 1. 3-Tier System Prompt Architecture
```
+-------------------------------------------------------------+
| Tier 1: Identity & Operational Core (Stable, Cache-Friendly)|
| - Concise direct tone, plain claims                         |
| - Tool-use enforcement & parallel batching                  |
| - Absolute paths, non-interactive flags, autonomy           |
+-------------------------------------------------------------+
| Tier 2: Rules for Memory & Skills                           |
| - Skills first (procedures, pitfalls) via skill_manage      |
| - Memory narrow exception (declarative global facts)        |
+-------------------------------------------------------------+
| Tier 3: Dynamic Context (Volatile / Per-Session)            |
| - CWD, OS, user info                                        |
| - Durable memory snippets (~/.hermes/memories/)             |
| - Available skills index (<available_skills>)               |
| - Workspace rules (AGENTS.md / CLAUDE.md)                   |
+-------------------------------------------------------------+
```

## 2. Gateway HTTP Configuration
- Config in `~/.hermes/.env`:
  ```env
  API_SERVER_ENABLED=true
  API_SERVER_KEY=my-secret-key
  API_SERVER_PORT=8642
  ```
- Command: `hermes gateway`
- Endpoint: `POST /v1/chat/completions` (OpenAI-compatible)
