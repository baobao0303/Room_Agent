---
name: hermes-research
description: "Structured technical research and architecture reporting skill using 3-tier system prompts and Hermes Gateway / CLI fallback."
---

# Hermes Research Skill (`hermes-research`)

Bộ kỹ năng thực hiện nghiên cứu chuyên sâu, phân tích so sánh kiến trúc và tự động xuất bản báo cáo Markdown chuẩn mực.

---

## 1. When to Use
- Khi cần nghiên cứu một công nghệ, thư viện, hoặc so sánh các phương án kiến trúc (ví dụ: REST vs EDA, Microservices vs Monolith).
- Khi Lead BA / Lead Dev cần tài liệu tham khảo kỹ thuật có căn cứ xác thực.

---

## 2. Quick Commands Reference

### Chạy Research Agent (Python):
```bash
python3 tools/research/research_agent.py "<Chủ đề nghiên cứu>" [output_path.md]
```
*(Kết quả tự động lưu vào `tools/research/<topic>.md`).*

### Chạy Research Agent (TypeScript / Node):
```bash
npx tsx tools/research/research_agent.ts "<Chủ đề nghiên cứu>" [output_path.md]
```
