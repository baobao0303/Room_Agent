---
name: harness2-orchestrator
description: Orchestrate Google Research Harness² (projects/harness2) for Supervisor self-learning, autonomous skill self-authoring, stage-by-stage Evals (PASS >= 98.5%), and Kev System One uncertainty/level checks across 3-Tier Memory.
version: 2.0.0
roles: [supervisor]
---

# Google Research Harness² & Self-Evolution Skill (`harness2-orchestrator`)

Kỹ năng trung tâm giúp **Supervisor** vận hành **Google Research Harness²** (`https://github.com/google-research/harness2` được cài sẵn tại `projects/harness2`) kết hợp với `tools/supervisor_harness2_engine.py` để:
1. **Tự học hỏi & Tự viết Skill mới (`self-author-skill`)** đáp ứng nhu cầu phát sinh của bản thân.
2. **Kiểm định Evals ở từng giai đoạn (`eval-stage`)** theo 3 trụ cột (`Golden Dataset`, `LLM-as-a-Judge`, `Guardrails`) với chuẩn tốt nghiệp **PASS $\ge$ 98.5%**.
3. **Tự động học lại bằng Harness² (`relearn-stage`)** khi Evals thất bại ($< 98.5\%$) qua chu trình đệ quy `INV` (Invariant) + `DOM` (Domain) $\to$ `COMPOSE` (ràng buộc sổ cái `Ledger R=4k, P=3k`).
4. **Dùng Kev System One (`check-uncertainty`)** để kiểm tra mức độ thành thạo (Level) và giải quyết sự phân vân ở bất kỳ giai đoạn nào.
5. **Đồng bộ Trí Nhớ 3 Tầng (3-Tier Memory)**: Working Memory $\to$ Short-Term Session Buffer $\to$ Long-Term Vector/SQL & Harness² Experience Library.
