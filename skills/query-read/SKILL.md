---
name: query-read
description: "High-precision query-based text search, markdown chunking, and directory tree inspector. Solves EISDIR errors and locates code contexts with BM25 ranking."
---

# Query Reader Skill (`query-read`)

Bộ kỹ năng tìm kiếm và đọc file thông minh dựa trên giải thuật BM25 Ranking và Semantic Chunking Markdown, giải quyết triệt để lỗi `EISDIR` khi agent duyệt thư mục.

---

## 1. When to Use
- Khi Agent cần xem cấu trúc thư mục mà không làm tràn context.
- Khi cần tìm kiếm đoạn code, spec hoặc tài liệu API theo từ khóa / câu hỏi tự nhiên.
- Khi không chắc chắn tên file chính xác (tránh đoán mò tên file).

---

## 2. Quick Commands Reference

### A. Xem cây thư mục an toàn:
```bash
python3 tools/query_reader.py <folder_path>
```

### B. Tìm kiếm ngữ cảnh / giải pháp kỹ thuật theo câu hỏi:
```bash
python3 tools/query_reader.py <target_path> "<câu hỏi hoặc từ khóa>"
```

### C. Xuất kết quả dạng JSON cho Agent xử lý tiếp:
```bash
python3 tools/query_reader.py <target_path> "<query>" -j
```
