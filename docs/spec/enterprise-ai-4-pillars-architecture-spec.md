# BẢN ĐẶC TẢ KỸ THUẬT HỆ THỐNG AI DOANH NGHIỆP: 4 TRỤ CỘT KIẾN TRÚC THỰC CHIẾN

- **Mã định danh**: `ARCH-SPEC-ENTERPRISE-AI-4-PILLARS-2026-V1`
- **Phiên bản**: `1.0.0` (Production-Grade Enterprise Blueprint)
- **Trạng thái**: `APPROVED` (Chuẩn hóa thực thi trên hệ sinh thái `Room_Agent` / SLPPC)
- **Phạm vi áp dụng**: Toàn bộ kiến trúc AI Tác tử Doanh nghiệp (RAG Engine, Multi-Agent Orchestration, 3-Tier Memory Architecture, EVOS Evaluation & Guardrails Engine)
- **Tiêu chuẩn cổng phát hành (Release Gate)**: Task Completion Rate $> 90\%$, EVOS Quality Pass Rate $> 98\%$

---

## 1. Tổng quan & Mục tiêu Chiến lược Hệ thống

### 1.1. Bối cảnh & Tầm quan trọng Chiến lược
Trong tiến trình hiện đại hóa hạ tầng công nghệ thông tin cấp doanh nghiệp, việc chuyển dịch từ các mô hình Chatbot đơn lẻ (đơn tác tử - *Single-Agent*) sang **Hệ thống Tác tử Thực chiến (*Enterprise Agentic System*)** là yêu cầu kiến trúc bắt buộc. Môi trường vận hành doanh nghiệp đòi hỏi khả năng xử lý các quy trình làm việc đa bước, tích hợp sâu và có tính logic cao. Kiến trúc đơn tác tử không đáp ứng được quy mô này, dẫn đến tỷ lệ thất bại lớn khi triển khai thực tế. Việc thiết lập hệ thống đa tác tử cấp doanh nghiệp định hình lại năng lực tự động hóa, tối ưu hóa hiệu suất vận hành và đảm bảo tính sẵn sàng cho môi trường sản xuất (*Production*).

### 1.2. Phân tích Hạn chế của Chatbot Truyền thống (Context Window Dilution)
Nguyên nhân cốt lõi khiến mô hình AI đơn lẻ thất bại khi giải quyết các bài toán doanh nghiệp phức tạp nằm ở hiện tượng **suy giảm và quá tải cửa sổ ngữ cảnh (*Context Window Dilution*)**:
- Khi một mô hình ngôn ngữ duy nhất phải đồng thời đảm nhận nhiều vai trò—từ phân tích yêu cầu, thiết kế kiến trúc, viết mã nguồn cho đến kiểm thử—ngữ cảnh bị phân tán nghiêm trọng.
- Trạng thái này dẫn đến hai nguy cơ kỹ thuật lớn:
  1. Mô hình rơi vào cơ chế **"học vẹt" (*Rote Memorization*)**.
  2. Phát sinh hiện tượng **bịa đặt thông tin (*Hallucination*)**.
- Kết quả đo lường thực tế chỉ ra rằng, đối với các tác vụ phức tạp, tỷ lệ hoàn thành mục tiêu của một chatbot đơn lẻ chỉ dừng lại ở mức **20%**.

### 1.3. Chỉ số Tác động & Mục tiêu Kỹ thuật (KPIs)

| Chỉ số Mục tiêu Kỹ thuật | Mô hình Đơn Tác tử (Single-Agent) | Hệ thống Đa Tác tử (Multi-Agent) | Tiêu chuẩn Ngưỡng Phát hành (Release Gate) |
| :--- | :--- | :--- | :--- |
| **Tỷ lệ hoàn thành tác vụ phức tạp** | 20% | **> 90%** | Yêu cầu bắt buộc đạt **> 90%** |
| **Tỷ lệ vượt qua kiểm thử chất lượng (Pass Rate)** | Không có cơ chế tự động | Được thẩm định qua EVOS Engine | **> 98%** (Đạt chuẩn đưa vào Production) |
| **Rủi ro bịa đặt thông tin (Hallucination Rate)** | Cao (Không kiểm soát) | **0% (Context-Bounded)** | Bắt buộc trích xuất đúng **3 context chunks** |
| **Khả năng duy trì trạng thái (Statefulness)** | Vô trạng thái (Stateless) | **3-Tier Dynamic Hydration** | Phục hồi 100% ngữ cảnh dự án/cá nhân hóa |

### 1.4. Kiến trúc Tổng thể 4 Trụ cột Nền tảng
Để đảm bảo tính toàn vẹn, độ tin cậy và khả năng mở rộng, hệ thống AI doanh nghiệp **BẮT BUỘC** phải được xây dựng dựa trên 4 phân hệ kiến trúc nền tảng:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│             KIẾN TRÚC HỆ THỐNG AI DOANH NGHIỆP: 4 TRỤ CỘT THỰC CHIẾN                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  [1. PHÂN HỆ RAG - THỦ THƯ SIÊU TỐC]           [3. PHÂN HỆ MEMORY 3 TẦNG]               │
│  ┌───────────────────────────────────────┐     ┌─────────────────────────────────────┐  │
│  │ • Chunking & Vector DB Indexing       │     │ • Tầng 1: Working Memory (RAM)      │  │
│  │ • Semantic Search (Top-K = 3 Chunks)  │◄───►│ • Tầng 2: Short-Term (Session)      │  │
│  │ • Context-Bounded Prompting (0% Bịa)  │     │ • Tầng 3: Long-Term DB + Hydration  │  │
│  └──────────────────┬────────────────────┘     └──────────────────┬──────────────────┘  │
│                     │                                             │                     │
│                     ▼                                             ▼                     │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │                [2. PHÂN HỆ MULTI-AGENT ARCHITECTURE (CÔNG TY THU NHỎ)]            │  │
│  │                                                                                   │  │
│  │   [PM Agent] ──(JSON Schema)──► [Coder Agent] ──(Artifact)──► [Tester Agent]      │  │
│  │   (Điều phối)                        ▲                        (Destructive Test)  │  │
│  │                                      └──(Error Stack Trace)─────────┤             │  │
│  │                                                                     ▼ (Pass)      │  │
│  │                                                             [Reviewer Agent]      │  │
│  │                                                             (Cross-Critique)      │  │
│  └──────────────────────────────────────┬────────────────────────────────────────────┘  │
│                                         │                                               │
│                                         ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │            [4. PHÂN HỆ EVALS & GUARDRAILS (EVOS ENGINE - RELEASE GATE)]           │  │
│  │  • Golden Dataset (Edge Cases Regression)   • LLM-as-a-Judge (Chấm điểm độc lập) │  │
│  │  • Real-time Inline Guardrails (Anti-Leak)  • Release Gate: PASS RATE > 98%       │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Phân hệ RAG (Retrieval-Augmented Generation)**: Cơ chế truy xuất tri thức nội bộ chuẩn xác, triệt tiêu rủi ro bịa đặt thông tin.
2. **Phân hệ Multi-Agent Architecture**: Mô hình chuyên môn hóa tác tử theo cấu trúc nhân sự tổ chức nhằm phân rã và xử lý triệt để tác vụ phức tạp.
3. **Phân hệ Memory Architecture**: Hệ thống trí nhớ 3 tầng duy trì trạng thái ngữ cảnh từ ngắn hạn đến dài hạn.
4. **Phân hệ Evals & Guardrails (EVOS Engine)**: Khung đánh giá chất lượng tự động và lớp bảo mật chặn đứng rủi ro an toàn thông tin.

> **Dẫn nhập Kiến trúc**: Nền tảng của một hệ thống AI doanh nghiệp tin cậy bắt đầu từ khả năng truy xuất và xử lý tri thức chuẩn xác. Phân hệ RAG đóng vai trò là điểm tựa dữ liệu cho toàn bộ các hoạt động xử lý tiếp theo.

---

## 2. Phân hệ RAG (Retrieval-Augmented Generation) - Tạo sinh Tăng cường Truy xuất

### 2.1. Bối cảnh & Tầm quan trọng Chiến lược
Các mô hình ngôn ngữ lớn (LLM) nguyên bản có xu hướng tự lấp đầy khoảng trống tri thức bằng cách học vẹt hoặc bịa đặt thông tin khi xử lý các dữ liệu chưa từng được huấn luyện. Phân hệ RAG được kiến thiết như một **"Thủ thư siêu tốc" (*High-Speed Retrieval Engine*)**, đóng vai trò trung gian truy xuất giữa LLM và kho dữ liệu nội bộ/tài liệu mật của doanh nghiệp. Phân hệ này loại bỏ hoàn toàn việc phụ thuộc vào trí nhớ gốc của mô hình, đảm bảo mọi đầu ra đều dựa trên dữ liệu thực tế.

### 2.2. Cơ chế Xử lý Dữ liệu & Tìm kiếm Semantic

```text
[Tài liệu Nội bộ / Quy trình Mật]
       │
       ▼ (1. Data Chunking & Embedding)
[Vector Database (Chỉ mục Vector cấu trúc)]
       │
       ▼ (2. Truy vấn User ➔ Semantic Search)
[Trích xuất CỨNG: Đúng 3 Context Chunks có điểm tương đồng cao nhất]
       │
       ▼ (3. Context-Bounded Prompting)
[LLM Tổng hợp câu trả lời DUY NHẤT từ 3 Chunks ➔ Triệt tiêu 100% Hallucination]
```

- **Chiến lược Xử lý Dữ liệu (Chunking & Vector DB)**: Toàn bộ văn bản quy trình, tài liệu kỹ thuật và dữ liệu mật nội bộ **BẮT BUỘC** phải trải qua quy trình băm nhỏ (*chunking*) thành các khối ngữ cảnh tối ưu, sau đó được nhúng (*embedding*) và lưu trữ cấu trúc trong Cơ sở dữ liệu Vector (*Vector DB*).
- **Quy trình Truy xuất Semantic Search**: Khi phát sinh truy vấn từ người dùng, động cơ tìm kiếm ngữ nghĩa (*semantic search*) quét toàn bộ không gian Vector để định vị chính xác độ tương đồng ngữ nghĩa. Hệ thống thiết lập giới hạn cứng: **chỉ trích xuất đúng 3 đoạn ngữ cảnh (3 context chunks)** có điểm số tương đồng cao nhất (`Top-K = 3`) để truyền tải cho LLM.

### 2.3. Nguyên tắc Chống Bịa đặt ("Nói có sách, mách có chứng")
- Việc giới hạn đầu vào ở **đúng 3 đoạn ngữ cảnh trích xuất** là giải pháp kỹ thuật tối ưu nhằm cân bằng giữa độ phủ (*recall*) và độ chính xác (*precision*), đồng thời ngăn chặn hiện tượng nhiễu ngữ cảnh (*context bloat*).
- Hệ thống ép buộc LLM hoạt động trong cơ chế **"Context-Bounded Prompting"**—chỉ được phép tổng hợp câu trả lời duy nhất từ thông tin chứa trong 3 đoạn ngữ cảnh này. Nếu thông tin không tồn tại trong 3 chunks, hệ thống bắt buộc từ chối trả lời thay vì suy đoán.
- Nguyên tắc *"Nói có sách, mách có chứng"* triệt tiêu hoàn toàn hiện tượng học vẹt và bịa đặt thông tin, đảm bảo tính minh bạch và độ tin cậy tuyệt đối của dữ liệu doanh nghiệp.

### 2.4. Bảng Tóm tắt Thông số Phân hệ RAG

| Thành phần Kỹ thuật | Cơ chế Hoạt động | Giới hạn Đầu ra Ràng buộc | Kết quả Cam kết Kiến trúc |
| :--- | :--- | :--- | :--- |
| **Data Chunking & Vector DB** | Băm nhỏ dữ liệu mật/nội bộ thành các Vector chunks và lưu trữ dạng chỉ mục | Lưu trữ tối ưu hóa tìm kiếm Vector | Chuẩn hóa kho tri thức enterprise |
| **Semantic Search Engine** | Tìm kiếm ngữ nghĩa dựa trên độ tương đồng Vector khi có truy vấn | **Trích xuất chính xác 3 đoạn ngữ cảnh (`Top-K = 3`)** | Định vị đúng ngữ cảnh liên quan nhất |
| **Context-Bound LLM Engine** | Chỉ tổng hợp câu trả lời dựa trên 3 đoạn ngữ cảnh được cung cấp | Không truy xuất bộ nhớ ngoài 3 chunks | **Loại bỏ hoàn toàn bịa đặt (Hallucination)** |

> **Dẫn nhập Kiến trúc**: Khi tri thức nội bộ đã được chuẩn hóa và truy xuất chính xác qua RAG, thách thức tiếp theo là tổ chức thực thi các quy trình nghiệp vụ đa bước. Điều này đòi hỏi sự tham gia của Phân hệ Đa Tác tử với cơ chế phân công chuyên biệt.

---

## 3. Phân hệ Kiến trúc Đa Tác tử (Multi-Agent Architecture)

### 3.1. Bối cảnh & Tầm quan trọng Chiến lược
Để xử lý một quy trình công việc phức tạp mà không làm quá tải cửa sổ ngữ cảnh, hệ thống áp dụng nguyên lý phân rã bài toán bằng **Phân hệ Đa Tác tử (*Multi-Agent Architecture*)**. Hệ thống được cấu trúc như một **"công ty thu nhỏ" (*micro-enterprise*)**, trong đó từng tác tử AI được tối ưu hóa cho một phạm vi trách nhiệm duy nhất, phối hợp với nhau qua các giao thức truyền nhận dữ liệu chặt chẽ.

### 3.2. Phân vai Chi tiết Các Tác tử (Agent Roles & SLPPC Mapping)

| Vai trò Tác tử (Enterprise Spec) | Ánh xạ trong `Room_Agent` (SLPPC) | Trách nhiệm Cốt lõi & Phạm vi Quyền hạn |
| :--- | :--- | :--- |
| **PM Agent** *(Project Manager Agent)* | `supervisor` + `pm` + `lead` | **Điều phối trung tâm**: Tiếp nhận yêu cầu phức tạp từ người dùng, phân tích cấu trúc, thẩm định tính khả thi và chia nhỏ bài toán thành các tác vụ nguyên tử (*atomic tasks* / *Zero-Search tasks*) để phân công đến các tác tử chuyên trách. |
| **Coder Agent** | `peer` (`peer1..4`, `peer_design`) | **Chuyên biệt hóa thực thi**: Tập trung 100% năng lực vào việc khởi tạo và phát triển mã nguồn (*source code*) trên cửa sổ ngữ cảnh tinh gọn dựa trên đúng đặc tả kỹ thuật do PM Agent chuyển giao. |
| **Tester Agent** | `qc` (*ISTQB 5-Stage Test Runner*) | **Kiểm thử phá hoại (*Destructive Testing*)**: Chủ động dò tìm lỗi biên (*edge cases*), điểm yếu bảo mật và các ngoại lệ logic của mã nguồn do Coder Agent khởi tạo thông qua thực thi test cơ học. |
| **Reviewer Agent** | `lead` (*Code Review*) + `qc` (*Audit Gate*) | **Phản biện chéo (*Cross-Critique / Peer Review*)**: Đánh giá tối ưu hóa mã nguồn, chuẩn mực kiến trúc (Strict Typing, Zero `any`) và tính chính xác của logic trước khi thông qua nghiệm thu. |

### 3.3. Quy trình Phối hợp & Chuyển giao Tác vụ (Workflow & Hand-off Mechanics)
Tiến trình vận hành giữa các tác tử tuân thủ **Quy trình Chuyển giao Dữ liệu Cấu trúc (*Structured Output Protocol*)** sử dụng định dạng **JSON Schema**:

```text
┌──────────────┐   1. JSON Schema Spec   ┌──────────────┐   2. Code Artifact   ┌──────────────┐
│   PM AGENT   │ ──────────────────────► │ CODER AGENT  │ ───────────────────► │ TESTER AGENT │
│ (Atomic Task)│                         │ (Source Code)│                      │ (Destructive)│
└──────────────┘                         └──────┬───────┘                      └──────┬───────┘
                                                ▲                                     │
                                                │ 3a. FAIL: Feedback / Retry Loop     │
                                                │     (Error Stack Trace JSON)        │
                                                └─────────────────────────────────────┤
                                                                                      │ 3b. PASS
                                                                                      ▼
                                         ┌──────────────┐   4. Cross-Critique  ┌──────────────┐
                                         │ TASK CLOSED  │ ◄─────────────────── │REVIEWER AGENT│
                                         │ (>90% Target)│     (Approved)       │ (Peer Review)│
                                         └──────────────┘                      └──────────────┘
```

1. **Phân rã & Đóng gói (PM $\rightarrow$ Coder)**: Khi **PM Agent** phân rã bài toán, yêu cầu kỹ thuật được đóng gói thành payload JSON chuẩn hóa (bao gồm `target_files`, `anchors`, `concrete_changes`, `acceptance_criteria`, `test_command`) gửi tới **Coder Agent**.
2. **Thực thi & Kích hoạt Kiểm thử (Coder $\rightarrow$ Tester)**: Sau khi hoàn tất viết code, **Coder Agent** tạo ra Artifact và tự động kích hoạt **Tester Agent**.
3. **Vòng lặp Phản hồi Sửa lỗi (Tester $\rightarrow$ Coder Feedback/Retry Loop)**: Nếu **Tester Agent** phát hiện lỗi trong quá trình kiểm thử phá hoại, một luồng phản hồi chứa thông tin lỗi chi tiết (*Error Stack Trace*) sẽ được gửi ngược lại cho **Coder Agent** để sửa lỗi (giới hạn trong trần vòng lặp *Turn Ceiling*).
4. **Phản biện Chéo & Nghiệm thu (Tester $\rightarrow$ Reviewer $\rightarrow$ Release)**: Sau khi vượt qua kiểm thử cơ học, **Reviewer Agent** tiến hành phản biện chéo lần cuối. Quy trình khép kín này đảm bảo tỷ lệ hoàn thành tác vụ phức tạp tăng vọt từ **20%** (ở mô hình đơn tác tử) lên **trên 90%**.

### 3.4. Chuẩn JSON Schema Chuyển giao Tác vụ (Structured Hand-off Contract)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "AgentHandoffEnvelope",
  "type": "object",
  "required": ["task_id", "from_role", "to_role", "status", "spec", "verification"],
  "properties": {
    "task_id": { "type": "string" },
    "from_role": { "enum": ["PM", "CODER", "TESTER", "REVIEWER"] },
    "to_role": { "enum": ["CODER", "TESTER", "REVIEWER", "RELEASE"] },
    "status": { "enum": ["ASSIGNED", "RESOLVED", "FAILED_RETRY", "APPROVED"] },
    "spec": {
      "type": "object",
      "required": ["target_files", "anchors", "concrete_changes", "acceptance_criteria", "test_command"],
      "properties": {
        "target_files": { "type": "array", "items": { "type": "string" } },
        "anchors": { "type": "array", "items": { "type": "string" } },
        "concrete_changes": { "type": "string" },
        "acceptance_criteria": { "type": "array", "items": { "type": "string" } },
        "test_command": { "type": "string" }
      }
    },
    "verification": {
      "type": "object",
      "properties": {
        "exit_code": { "type": "integer" },
        "error_stack_trace": { "type": "string" },
        "retry_count": { "type": "integer", "maximum": 3 }
      }
    }
  }
}
```

> **Dẫn nhập Kiến trúc**: Việc phối hợp giữa các tác tử đòi hỏi hệ thống phải duy trì thông tin trạng thái nhất quán theo thời gian. Phân hệ Trí nhớ 3 Tầng được tích hợp để giải quyết triệt để bài toán lưu trữ ngữ cảnh này.

---

## 4. Phân hệ Kiến trúc Trí nhớ 3 Tầng (3-Tier Memory Architecture)

### 4.1. Bối cảnh & Tầm quan trọng Chiến lược
Bản chất vận hành nguyên bản của các mô hình ngôn ngữ lớn là **vô trạng thái (*stateless*)**—mọi dữ liệu phiên làm việc sẽ xóa bỏ hoàn toàn khi kết thúc kết nối. Để biến hệ thống AI thành một cộng sự đắc lực có khả năng thấu hiểu ngữ cảnh tích lũy của doanh nghiệp, kiến trúc **BẮT BUỘC** phải tích hợp **Phân hệ Trí nhớ 3 Tầng (*3-Tier Memory Architecture*)**.

### 4.2. Đặc tả Chi tiết 3 Tầng Trí nhớ

- **Tầng 1: Working Memory (Trí nhớ làm việc)**:
  - Là không gian xử lý tức thời trong cửa sổ ngữ cảnh (*Context Window*) của LLM.
  - Chứa trực tiếp prompt hiện tại, 3 đoạn ngữ cảnh trích xuất từ RAG, dữ liệu đầu vào và các tham số điều khiển tức thời (được tối ưu hóa dưới 30k tokens qua RTK Proxy).
- **Tầng 2: Short-Term Memory (Trí nhớ ngắn hạn)**:
  - Duy trì trạng thái của phiên làm việc hiện hành (*Session Summary* / `bmad/rooms/` & `docs/AGENT_PROGRESS.md`).
  - Tự động đóng gói và tóm tắt diễn tiến, các quyết định đã thực hiện và lịch sử tương tác trong suốt phiên.
- **Tầng 3: Long-Term Memory (Trí nhớ dài hạn)**:
  - Được lưu trữ bền vững trên hệ quản trị cơ sở dữ liệu (*External Database*: Floci DynamoDB / S3 / Harness Learn Store).
  - Ghi nhớ thói quen cá nhân, phong cách lập trình, các bẫy lỗi lịch sử (*past pitfalls*), quy chuẩn doanh nghiệp và kiến trúc dự án qua thời gian.

### 4.3. Cơ chế Đồng bộ & Phục hồi Ngữ cảnh (Dynamic Hydration)

```text
[Khởi tạo Phiên làm việc Mới (Session Start)]
       │
       ├──► 1. Truy vấn Long-Term Memory (Database) theo [User ID / Project ID]
       │       (Lấy: Quy chuẩn doanh nghiệp, Kiến trúc dự án, Thói quen lập trình, Bẫy lỗi cũ)
       │
       ├──► 2. Kết hợp Short-Term Memory (Session Summary gần nhất)
       │
       └──► 3. DYNAMIC HYDRATION ──► Bơm trực tiếp vào Working Memory (Context Window)
                                     (Sẵn sàng 100% ngữ cảnh ngay từ giây đầu tiên)
```

Khi một phiên làm việc mới được khởi tạo, hệ thống thực hiện cơ chế **Dynamic Hydration**: truy vấn Long-Term Memory từ Database dựa trên `User ID` / `Project ID` để nạp (*hydrate*) các tham số cấu hình, thói quen và kiến trúc dự án vào Working Memory. Nhờ cơ chế này, ngay cả khi quay lại sau 1 tháng, hệ thống AI vẫn duy trì sự hiểu biết chính xác về phong cách làm việc và cấu trúc hệ thống như ngày đầu tiên mà không cần nạp lại ngữ cảnh thủ công.

### 4.4. Bảng So sánh 3 Tầng Trí nhớ

| Tầng Trí nhớ | Vị trí Lưu trữ / Bản chất Kỹ thuật | Ánh xạ trong `Room_Agent` | Chức năng Vận hành Chính | Thời gian Tồn tại Dữ liệu |
| :--- | :--- | :--- | :--- | :--- |
| **Working Memory** | Context Window (RAM/In-Memory) | Active Agent Context (<30k tokens, RTK) | Chứa câu lệnh và ngữ cảnh xử lý tức thời | Theo từng truy vấn (*Prompt-level*) |
| **Short-Term Memory** | Session State / Dynamic Summary | `bmad/rooms/`, `docs/AGENT_PROGRESS.md` | Tóm tắt tiến trình và diễn biến toàn bộ phiên | Theo độ dài phiên làm việc (*Session-level*) |
| **Long-Term Memory** | External Database (Relational/NoSQL) | Harness DB (Floci DynamoDB/S3) & Learn Store | Lưu giữ thói quen, quy chuẩn, kiến trúc dự án | Lưu trữ bền vững vĩnh viễn (*Persistent*) |

> **Dẫn nhập Kiến trúc**: Khi các phân hệ RAG, Multi-Agent và Memory đã hoàn thiện năng lực xử lý, hệ thống cần một cơ chế kiểm soát chất lượng và an toàn thông tin trước khi chính thức đưa vào môi trường vận hành thực tế.

---

## 5. Phân hệ Đánh giá & An toàn Hệ thống (Evaluation & Guardrails - EVOS Engine)

### 5.1. Bối cảnh & Tầm quan trọng Chiến lược
Rào cản lớn nhất khiến các dự án AI dừng lại ở giai đoạn thử nghiệm (*Demo*) là rủi ro về độ ổn định và an toàn thông tin. Phân hệ **EVOS Engine** đóng vai trò như một **"kỳ thi tốt nghiệp tự động"**, thiết lập đường ray kiểm soát chất lượng toàn diện để đảm bảo hệ thống đạt chuẩn vận hành công nghiệp trước khi đưa ra thị trường.

### 5.2. Ba Thành phần Cốt lõi & Quy trình Tích hợp (Inline & Pipeline Integration)
Hệ thống tích hợp 3 lớp kiểm soát thành một quy trình thống nhất bao gồm cả kiểm thử thời gian thực (*Inline Filter*) và kiểm thử tự động trong luồng triển khai (*CI/CD Pipeline*):

```text
                  ┌───────────────────────────────────────────────────────┐
                  │           EVOS ENGINE & GUARDRAILS PIPELINE           │
                  └───────────────────────────┬───────────────────────────┘
                                              │
        ┌─────────────────────────────────────┼─────────────────────────────────────┐
        ▼ (1. Real-time Inline)               ▼ (2. CI/CD Regression)               ▼ (3. Independent Scoring)
┌───────────────────────────┐     ┌───────────────────────────┐     ┌───────────────────────────┐
│   INLINE GUARDRAILS       │     │      GOLDEN DATASET       │     │      LLM AS A JUDGE       │
│ • Chống Prompt Injection  │     │ • Hàng nghìn kịch bản khó │     │ • Giám khảo AI độc lập    │
│ • Chặn mã độc & Anti-Leak │     │ • Edge cases & Bad inputs │     │ • Chấm điểm định lượng    │
│ • Bảo vệ dữ liệu mật      │     │ • Regression Test tự động │     │   logic, chính xác, AC    │
└─────────────┬─────────────┘     └─────────────┬─────────────┘     └─────────────┬─────────────┘
              └─────────────────────────────────┼─────────────────────────────────┘
                                                ▼
                              ┌───────────────────────────────────┐
                              │     RELEASE GATE VERIFICATION     │
                              │   Yêu cầu: PASS RATE >= 98.0%     │
                              └─────────┬───────────────┬─────────┘
                           (< 98%: BLOCK)               (>= 98%: ALLOW)
                                        ▼               ▼
                              [CHẶN TRIỂN KHAI]   [PRODUCTION DEPLOY]
```

1. **Golden Dataset (Bộ dữ liệu chuẩn hóa)**:
   - Tập hợp hàng nghìn kịch bản hóc búa, biên dữ liệu phức tạp (*edge cases*) và các tình huống diễn biến xấu được lưu trữ sẵn để chạy kiểm thử hồi quy (*Regression Testing*) tự động trong quy trình CI/CD.
2. **LLM As A Judge (Thẩm định tự động)**:
   - Sử dụng một mô hình AI độc lập chuyên biệt làm giám khảo (kết hợp cùng Kev System One & QC Verifier), chấm điểm định lượng độ chính xác, tính logic và mức độ tuân thủ yêu cầu của kết quả đầu ra một cách khách quan (*"Never let the AI verify its own done"*).
3. **Guardrails (Thẩm định thời gian thực - Inline Filtering)**:
   - Tấm khiên an ninh chạy trực tuyến (*real-time inline*), phân tích và chặn đứng ngay lập tức các nguy cơ chứa mã độc, hành vi can thiệp trái phép (*prompt injection*), và sự cố rò rỉ dữ liệu bảo mật của doanh nghiệp (`scripts/anti_leak_sentinel.py`, `tools/slppc_flow_guard.py`).

### 5.3. Tiêu chuẩn Phát hành Hệ thống (Release Gate)
Hệ thống thiết lập ngưỡng kiểm soát tuyệt đối:
- Chỉ khi toàn bộ hệ thống vượt qua bộ kịch bản kiểm thử của **EVOS Engine** và đạt điểm số **Pass Rate từ 98% trở lên ($\ge 98\%$)**, đồng thời đảm bảo **0% vi phạm Guardrails/Anti-Leak**, quy trình CI/CD mới cấp phép bấm nút đẩy hệ thống ra môi trường sản xuất thực chiến (*Production*).

---

## 6. Tổng kết Kiến trúc & Ma trận Đối chiếu Thực thi

Bản đặc tả kỹ thuật hệ thống AI doanh nghiệp là sự kết hợp hữu cơ của 4 trụ cột cốt lõi:

| Trụ cột Kiến trúc | Giải pháp Kỹ thuật Cốt lõi | Bài toán Doanh nghiệp được Giải quyết | Cam kết SLA / KPI |
| :--- | :--- | :--- | :--- |
| **1. Phân hệ RAG** | Chunking + Vector DB + Semantic Search (**Đúng 3 Context Chunks**) + Context-Bounded Prompting | Triệt tiêu hiện tượng học vẹt và bịa đặt thông tin (*Hallucination*) | **0% Bịa đặt ngoài ngữ cảnh** |
| **2. Multi-Agent Architecture** | Chuyên môn hóa 4 vai trò (**PM, Coder, Tester, Reviewer**) + JSON Schema Hand-off + Retry Loop | Giải quyết triệt để hiện tượng loãng ngữ cảnh (*Context Window Dilution*) | Hoàn thành tác vụ phức tạp **> 90%** (so với 20% ở Single-Agent) |
| **3. Memory Architecture** | Trí nhớ 3 tầng (**Working, Short-Term, Long-Term**) + Cơ chế **Dynamic Hydration** | Khắc phục bản chất vô trạng thái (*Stateless*) của LLM qua thời gian | **100% Phục hồi ngữ cảnh** sau nhiều tháng gián đoạn |
| **4. EVOS Engine & Guardrails** | **Golden Dataset** + **LLM-as-a-Judge** + **Real-time Inline Guardrails** | Đảm bảo độ ổn định công nghiệp và an toàn thông tin tuyệt đối trước khi lên Production | **Pass Rate > 98%** tại cổng Release Gate |

Việc tuân thủ nghiêm ngặt bản đặc tả `ARCH-SPEC-ENTERPRISE-AI-4-PILLARS-2026-V1` này là điều kiện tiên quyết giúp doanh nghiệp làm chủ công nghệ, đưa các hệ thống AI tác tử thực chiến vào vận hành ổn định, an toàn và đạt hiệu suất tối ưu.
