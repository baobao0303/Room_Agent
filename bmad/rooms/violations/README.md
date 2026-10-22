# 📜 SỔ CÁI BIÊN BẢN VI PHẠM KỶ LUẬT ĐIỀU HÀNH SLPPC (VIOLATIONS LEDGER)

> Thư mục tập trung ghi nhận toàn bộ các biên bản xử phạt kỷ luật, rào cản thẩm quyền bị phá vỡ và sai phạm quy trình trong mô hình điều hành đa Agent **SLPPC** (Supervisor - Lead - PM - Peer - QC).

---

## 1. Cơ Chế Lập Biên Bản Tự Động (Automated Flow Guard)
Biên bản được khởi tạo theo 2 phương thức:
1. **Chủ động qua lệnh CLI**: Bất kỳ Role nào phát hiện vi phạm có bằng chứng đều có quyền triệu tập biên bản kỷ luật qua:
   ```bash
   python3 tools/agent_reprimand.py \
     --from-role "Supervisor" \
     --to-role "Lead" \
     --violation "role_trespass" \
     --task-id 4110 \
     --evidence "Lead tự gõ code trực tiếp" \
     --message "Lead phải phân rã Zero-Search Task cho Peer, cấm ôm code" \
     --penalize
   ```
2. **Tự động qua Heartbeat Watchdog**:
   - `tools/slppc_flow_guard.py` chạy định kỳ qua Heartbeat quét rà soát các hành vi:
     * **Lead ôm code (`role_trespass`)**: Lead tự sửa code sản phẩm thay vì giao Peer.
     * **Dev tự đóng việc (`premature_close`)**: Peer chuyển task sang Closed mà chưa qua QC.
     * **Bỏ qua cổng PM (`pm_bypass`)**: Mở task/epic mà không qua đánh giá Khả thi & Phù hợp của PM Agent.
     * **Giao việc cẩu thả (`vague_specs`)**: Giao task thiếu 5 trường Zero-Search Mandate.

---

## 2. Quy Chuẩn Đặt Tên Biên Bản (Taxonomy)
Mọi biên bản được lưu trữ dưới định dạng:
```text
violation_<task_id>_<from_role>_to_<to_role>_<YYYYMMDD_HHMMSS>.md
```

---

## 3. Chế Tài Kỷ Luật (Sanctions Matrix)
| Mức độ | Hành vi sai phạm | Chế tài áp dụng |
| :--- | :--- | :--- |
| **Nghiêm trọng (Red)** | Role trespass (Lead ôm code, Supervisor sửa tính năng), Bypass PM Gate | Giáng task về `Active/Blocked`, phạt thu hồi task, bắt buộc giải trình |
| **Nặng (Orange)** | Strict Typing Gate (dùng `any`, `unknown`, `||`), QC lơ là nghiệm thu | REJECT task ngay lập tức, trừ điểm uy tín trong Harness DB |
| **Trung bình (Yellow)** | Giao task thiếu 5 trường Zero-Search, nộp code thiếu unit test | Yêu cầu Lead viết lại spec định lượng trong vòng 1 turn |
| **Nhẹ (Blue)** | Tự học: nạp bài học sơ sài, thiếu bằng chứng kiểm thử | Lọc thanh trừng qua `harness_learning_search.py audit --prune` |
