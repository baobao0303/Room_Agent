# Đặc Tả Kiến Trúc Điều Phối Đa Tác Nhân SLP (Supervisor - Lead - Peer)

> **Tài liệu tham chiếu gốc**: [Agent Orchestration Multi-Agent SLP](https://vhlam.com/article/agent-orchestration-multi-agent-slp)  
> **Hệ thống áp dụng**: Paseo Multi-Agent Orchestrator & Harness State Engine  
> **Phiên bản**: 1.0.0 | **Ngày ban hành**: 2026-10-16  

---

## 1. Bối Cảnh & Vấn Đề Cốt Lõi (Context & Failure Analysis)

### 1.1 Thách thức trong hệ thống phức tạp
Trong các dự án kỹ thuật quy mô lớn (hạ tầng vi dịch vụ, monorepo micro-frontend, phụ thuộc dọc - *vertical dependencies*):
- Các agent đơn lẻ (Single-agent) hoặc mô hình bầy đàn tự do (Unstructured Swarm) nhanh chóng cạn kiệt Context Window (128k - 200k tokens).
- Xuất hiện hiện tượng phân mảnh trạng thái (State Drifting), tranh chấp quyền sửa mã nguồn và ảo giác suy luận khi phải xử lý đồng thời từ kiến trúc cấp cao đến chi tiết từng dòng code.

### 1.2 Sự thất bại của mô hình điều phối cũ (Pre-Solve Antipattern)
Mô hình Main Agent ➔ Sub-Agents truyền thống thường gặp lỗi cốt tử:
- **Áp đặt giải pháp cứng (*Pre-solve*)**: Main agent tự giả định kiến trúc, áp đặt cách giải quyết chi tiết xuống sub-agent.
- **Giải quyết phần ngọn**: Khi sub-agent gặp lỗi thực tế từ môi trường (runtime/build), thay vì điều chỉnh lại kiến trúc sai lầm ở gốc, sub-agent bị ép phải viết các bản vá tạm bợ (monkey patch).
- **Hao phí Token & Vòng lặp vô tận**: Sub-agent không có quyền lật lại quyết định sai của Main agent, dẫn đến việc tranh cãi hoặc lặp lại lỗi cũ.

---

## 2. Kiến Trúc Nền Tảng (Paseo Primitives & Custom Orchestration)

Mô hình **SLP (Supervisor - Lead - Peer)** vận hành trực tiếp trên các khối nguyên thủy (*primitives*) của Paseo:
1. **Rooms**: Không gian cô lập ngữ cảnh cho từng phân hệ/nhiệm vụ.
2. **Sessions**: Tiến trình thực thi độc lập của từng agent.
3. **Messaging**: Giao thức truyền tin có cấu trúc, bất đồng bộ và hai chiều.

> **Nguyên tắc**: Bỏ qua các cơ chế auto-orchestration dựng sẵn của framework; thiết lập hệ thống phân quyền, kiểm soát trạng thái và quy trình giao tiếp nghiêm ngặt theo mô hình SLP.

---

## 3. Ma Trận Phân Quyền & Vai Trò (Role & Authority Matrix)

Mô hình xác định rõ ràng quyền hạn và nghĩa vụ của từng thực thể:  
`"SLP không phải là role-play cho agent - đó là ranh giới quyền hạn thực tế."`

```text
       ┌───────────────┐
       │     Human     │  (Định hướng bài toán lõi, ưu tiên đánh đổi)
       └───────┬───────┘
               │ Chỉ thị / Giám sát tối cao
               ▼
       ┌───────────────┐
       │  Supervisor   │  (Scope & Intent Guard, Điều phối tài nguyên chung)
       └───────┬───────┘
               │ Điều phối phòng / Bàn giao
               ▼
       ┌───────────────┐
       │     Lead      │  (Kiến trúc sư, Trạng thái tập trung, Nghiệm thu)
       └───────┬───────┘
               │ Phân quyền sở hữu / Giao việc 3 phần
               ▼
       ┌───────────────┐
       │     Peer      │  (Thực thi chuyên môn: Code, Audit, Refactor)
       └───────────────┘
```

### 3.1 Human (Con người)
- Xác định bài toán nghiệp vụ lõi và tiêu chí thành công.
- Ra quyết định cuối cùng đối với các đánh đổi mang tính chiến lược (Chi phí vs Thời gian vs Độ phức tạp).
- Can thiệp định hướng khi hệ thống chạm ranh giới bế tắc.

### 3.2 Supervisor (Scope & Intent Guard)
- **Quyền hạn**:
  - Giám sát đa phạm vi (*cross-room*), bảo vệ toàn vẹn phạm vi công việc (*scope boundary*).
  - Điều phối tài nguyên tính toán dùng chung (hạn ngạch LLM, CPU, quota benchmark).
  - Làm cầu nối chuyển ngữ hai chiều giữa chỉ đạo của Human và ngôn ngữ kỹ thuật của Lead.
- **Ranh giới**: Không can thiệp vào chi tiết kỹ thuật nội bộ hoặc viết mã nguồn thay cho Lead/Peer.

### 3.3 Lead (Technical Architect & Room Coordinator)
- **Quyền hạn**:
  - Điều phối toàn diện bên trong Room; nắm giữ trạng thái tập trung (*central state*).
  - Phân chia quyền sở hữu (*ownership*) từng module cho từng Peer cụ thể.
  - Xử lý xung đột phụ thuộc chéo (*dependency conflicts*) giữa các Peer.
  - Nghiệm thu tích hợp mã nguồn trước khi bàn giao lại cho Supervisor.
- **Trách nhiệm**: Lắng nghe và thẩm định các phản biện kỹ thuật có bằng chứng từ Peer để điều chỉnh bản thiết kế.

### 3.4 Peer (Domain Technical Executor)
- **Quyền hạn**:
  - Sở hữu hoàn toàn phán đoán kỹ thuật trong phạm vi module được giao.
  - Trực tiếp khảo sát, viết mã, chạy test và benchmark.
  - **Quyền lật lại thiết kế (*Right to Challenge*)**: Được phép từ chối hoặc yêu cầu Lead thay đổi giải pháp kiến trúc nếu phát hiện lỗ hổng hoặc bất cập trong thực tế thi công.
- **Ràng buộc**: Mọi phản biện bắt buộc phải đi kèm **bằng chứng thực nghiệm** (xem Mục 5).

---

## 4. Quản Lý Trạng Thái & Quyền Sở Hữu Đơn Nhất (Single-Ownership Invariant)

### 4.1 Bất biến vận hành cốt lõi (The Golden Invariant)
> **"Một phạm vi mã nguồn/nhiệm vụ đang thay đổi chỉ có DUY NHẤT một owner tại một thời điểm, cho tới khi được bàn giao chính thức."**

- **Tuyệt đối cấm sửa chéo (No Cross-Editing)**: Không agent nào được phép can thiệp hoặc sửa đổi file/module đang thuộc quyền sở hữu của agent khác.
- **Bàn giao minh bạch (Explicit Handoff)**: Trạng thái chỉ chuyển giao khi có bản ghi bàn giao rõ ràng (ghi nhận file thay đổi, kết quả test, điểm nghẽn còn lại).

### 4.2 Phân định tầng trạng thái
- **Trạng thái tập trung (Central State - Lead sở hữu)**:
  - Bản đồ kiến trúc hệ thống, ranh giới các module.
  - Ma trận phụ thuộc (Dependency Graph) và danh sách task đang phân bổ.
- **Trạng thái chuyên biệt (Local/Private State - Peer sở hữu)**:
  - AST, DOM, hàm nội bộ, logic chi tiết của component được giao.
  - Lịch sử thử nghiệm, kết quả profiling cục bộ.

---

## 5. Cơ Chế Giao Tiếp & Phản Biện Có Bằng Chứng (Evidence-Backed Challenge)

### 5.1 Quy tắc truyền tin hai chiều
- Luồng chỉ đạo: `Supervisor ➔ Lead ➔ Peer`.
- Supervisor có thể quan sát hoặc trao đổi trực tiếp với Peer nhằm nắm bắt tình hình thực tế, **nhưng mọi thay đổi về phương hướng giải pháp bắt buộc phải cập nhật ngược về Lead** để đồng bộ trạng thái tổng thể.

### 5.2 Cấu trúc giao việc chuẩn 3 phần (3-Part Task Delegation)
Khi Lead giao task cho Peer, bản đặc tả bắt buộc chia làm 3 phần rõ rệt:
1. **Mục tiêu tối hậu (*Ultimate Goal*)**: Mục đích cuối cùng cần đạt được (ví dụ: *Render danh sách 10.000 bản ghi mượt mà không rò rỉ bộ nhớ*).
2. **Ràng buộc cứng (*Hard Constraints*)**: Những giới hạn không được phép phá vỡ (ví dụ: *Dùng TDS UI tokens, không thêm thư viện ngoài, tương thích Angular 18*).
3. **Giải pháp gợi ý tạm thời (*Suggested Temporary Path*)**: Hướng đi phác thảo ban đầu từ Lead để Peer tham khảo, không có tính ép buộc.

### 5.3 Kỷ luật phản biện bằng chứng (Evidence Discipline)
- **Cấm phản biện cảm tính**: Nghiêm cấm các cuộc thảo luận lý thuyết suông gây lãng phí token và trôi ngữ cảnh.
- **Điều kiện chấp nhận phản biện**: Peer chỉ được phép đề xuất thay đổi kiến trúc của Lead khi cung cấp tối thiểu một trong các bằng chứng sau:
  - Log lỗi biên dịch hoặc Unit Test thất bại xác thực tính bất khả thi.
  - Kết quả đo lường hiệu năng/benchmark thực tế (CPU spike, memory leak, frame drops).
  - Tranh chấp phụ thuộc vòng lặp (Circular dependency) không thể phá vỡ ở tầng hiện tại.

---

## 6. Quy Trình Vận Hành 5 Bước (Lifecycle Workflow)

```text
┌────────────────┐      ┌────────────────┐      ┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│ 1. Lead Phân Rã│ ───► │ 2. Peer Khảo Sát│ ───► │ 3. Lead Thẩm Định│ ───► │ 4. Tích Hợp &  │ ───► │ 5. Better-SLP  │
│   & Ấn Định    │      │    & Thi Công  │      │    Chứng Cứ    │      │    Nghiệm Thu  │      │    Tiến Hóa    │
└────────────────┘      └────────────────┘      └────────────────┘      └────────────────┘      └────────────────┘
```

1. **Bước 1 - Phân bổ & Gán quyền**: Lead bóc tách yêu cầu từ Supervisor, lập bản đồ module, gán Single-Ownership cho từng Peer qua Task Delegation 3 phần.
2. **Bước 2 - Khảo sát & Thi công**: Peer nhận quyền, thực thi mã nguồn, chạy kiểm thử thực tế. Nếu giải pháp gợi ý của Lead gặp lỗi gốc, Peer thu thập bằng chứng và kích hoạt quyền phản biện.
3. **Bước 3 - Thẩm định & Tái cấu trúc**: Lead đánh giá bằng chứng từ Peer. Nếu bằng chứng hợp lệ, Lead cập nhật lại Central Plan, điều chỉnh ranh giới module và tái phân bổ.
4. **Bước 4 - Tích hợp & Nghiệm thu**: Peer hoàn tất thi công; Lead nghiệm thu thực tế dựa trên mã nguồn sạch, green tests và tiêu chí chấp nhận (AC).
5. **Bước 5 - Better-SLP (Tinh gọn liên tục)**: Sử dụng Telemetry hệ thống (tần suất xung đột code, số lần review vô hiệu, số vòng phản biện) để tự động cắt giảm các tầng trung gian không cần thiết, tối ưu hóa tốc độ xuất xưởng.

---

## 7. Mở Rộng SLPC Trong Paseo Project (Harness & Quality Gate Integration)

Dự án Paseo mở rộng mô hình SLP thành **SLPC** bằng việc bổ sung vai trò thứ 4 độc lập: **QC (Quality Gate & Test Architect)**:

| Vai trò | Phân vị SLP | Nhiệm vụ chính trong Paseo |
|---|---|---|
| **Supervisor** | SLP Supervisor | Quản trị intent, chi phí LLM, phân bổ Work Item trên Harness DB (`harness_manager.py`). |
| **Lead** | SLP Lead | Kiến trúc monorepo Rsbuild, Module Federation, duyệt PR, bảo vệ ranh giới module. |
| **Peer** | SLP Peer | Lập trình Angular 18, áp dụng TDS Tokens, viết mã nguồn sạch tại `projects/`. |
| **QC** | SLPC Extension | Cổng kiểm định độc lập Gate 4: Sinh ISTQB 5-Stage Unit Tests (`tools/qc_test_generator.py`), xác nhận AC trước khi đóng Work Item (`Closed`). |

---

## 8. Kết Luận & Quy Tắc Ghi Nhớ
1. Phân quyền dựa trên năng lực thực tế và bằng chứng, không dựa trên hội thoại nhập vai.
2. Một vùng thay đổi = Một chủ sở hữu duy nhất.
3. Phản biện cần số liệu thực nghiệm; cấm suy diễn lý thuyết.
4. Lead sở hữu bức tranh tổng thể; Peer sở hữu chi tiết chuyên môn.
5. Tiến hóa liên tục (Better-SLP) bằng cách loại bỏ ma sát quy trình.
