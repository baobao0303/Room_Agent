# ĐẶC TẢ KỸ THUẬT: SHOP_USER_LIST CONTEXT & QUY TRÌNH PHẢN BIỆN SLPC (PEER-LEAD REVIEW LOOP)

> **Mã đặc tả**: `SPEC-CRM-CONTEXT-SUL-2026`  
> **Phiên bản**: `1.0.0`  
> **Trạng thái**: `APPROVED`  
> **Phạm vi**: `projects/wicx-crm-fe/apps/app-shell/src/app/pages/setting/provider/context.provider.ts`  
> **Áp dụng**: Supervisor, Lead Dev, Peer Dev (1..4), Peer Design, QC  

---

## 1. BỐI CẢNH & HIỆN TRẠNG KỸ THUẬT (TECHNICAL OVERVIEW)

### 1.1. Vị trí & Interface Contract
- **File nguồn**: `projects/wicx-crm-fe/apps/app-shell/src/app/pages/setting/provider/context.provider.ts`
- **Injection Token**: `WI_USER_CONTEXT` từ thư viện `@wi-mfes/context`.
- **Interface chuẩn** (`@wi-mfes/context/models/user-context.interface.d.ts`):
  ```typescript
  import { Observable } from 'rxjs';

  export interface WIUserContext<T = unknown> {
    readonly currentUser: T | null;
    readonly user$: Observable<T | null>;
    readonly shopUserList$: Observable<T | null>;
  }
  ```

### 1.2. Hiện trạng mã nguồn & Nợ kỹ thuật
Hiện tại tại dòng 104-111 của `context.provider.ts`:
```typescript
// chỗ này tạm thời để vậy -> có api thì thêm call api 
return {
  get currentUser() {
    return getUser();
  },
  user$: of(getUser()),
  shopUserList$: of({ shopUsers: [], totalUser: 1 }),
};
```
- **Nợ kỹ thuật**: Dữ liệu `shopUserList$` đang trả về giá trị mock tĩnh `{ shopUsers: [], totalUser: 1 }` bọc trong `of()`.
- **Lý do**: Backend CRM/Account API chưa hoàn tất endpoint cung cấp danh sách nhân viên theo cửa hàng (`shopId`).
- **Rủi ro**: Nếu Peer tự ý chế mock hoặc gọi API giả định không có trong swagger/postman, hệ thống sẽ gãy runtime hoặc gây lỗi mạng 404 khi deploy staging.

---

## 2. KIẾN TRÚC MỤC TIÊU KHI CÓ API BACKEND (FUTURE TARGET ARCHITECTURE)

Khi Backend chính thức cung cấp API danh sách người dùng thuộc shop, quy trình thay thế mock phải tuân thủ nghiêm ngặt:

### 2.1. DTO Contract
```typescript
export interface ShopUserDto {
  id: string | number;         // ID bản ghi nhân viên trong shop (ShopUserDto.id)
  userId: string | number;     // ID tài khoản người dùng (Account User ID)
  fullName: string;
  userName: string;
  role: string;
  phone?: string;
  email?: string;
  avatarUrl?: string;
  isActive: boolean;
}

export interface ShopUserListResponse {
  shopUsers: ShopUserDto[];
  totalUser: number;
}
```

### 2.2. Nguồn Quản Trị State: Tái Sử Dụng `MemberStore`
Dữ liệu nhân viên thực tế trong hệ thống ĐÃ ĐƯỢC QUẢN TRỊ TẬP TRUNG trong Signal Store:
- **Thư mục**: `projects/wicx-crm-fe/libs/features/member`
- **Store**: `MemberStore` (`libs/features/member/data-access/src/stores/member.store.ts`), export từ `@wicx/features/member`.
- **Computed Selectors có sẵn**:
  - `memberStore.employeeList()`: Signal trả về danh sách `Employee[]` đã được store chuẩn hóa.
  - `memberStore.totalEmployees()`: Signal trả về `total` nhân viên.
- **NGUYÊN TẮC KIẾN TRÚC BẮT BUỘC (CRITICAL DIRECTIVE)**:
  Tuyệt đối KHÔNG inject `MemberService` thô để gọi lại API server và tự viết hàm mapping thủ công dài dòng. BẮT BUỘC inject trực tiếp `MemberStore` (tương tự như `AccountStore`), đọc tín hiệu từ `memberStore.employeeList` và `memberStore.totalEmployees` để chuyển đổi sang Observable cho `shopUserList$`.

### 2.3. Hiện Thực Hóa Tích Hợp `MemberStore` Trong `context.provider.ts`
```typescript
import { Provider, Optional, Injector, computed } from '@angular/core';
import { toObservable } from '@angular/core/rxjs-interop';
import { of } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import { LocalStorage, AUTH_STORAGE_KEYS } from '@wicx/core';
import { AccountStore } from '@wicx/features/account';
import { MemberStore, Employee } from '@wicx/features/member';
import { WI_USER_CONTEXT, WIUserContext } from '@wi-mfes/context';

// Trong useFactory của WI_USER_CONTEXT:
useFactory: (
  storage: LocalStorage,
  accountStore: InstanceType<typeof AccountStore>,
  memberStore?: InstanceType<typeof MemberStore> | null,
  injector?: Injector | null
): WIUserContext<any> => {
  const getUser = () => { ... };

  // Đọc danh sách trực tiếp từ MemberStore
  const getShopUsers = () => {
    const list: Employee[] = memberStore?.employeeList?.() || [];
    const total: number = memberStore?.totalEmployees?.() ?? list.length;

    const shopUsers = list.map((item) => ({
      id: item.shopUserId != null ? item.shopUserId : (item as any).id,
      userId: item.accountUserId != null && String(item.accountUserId).trim() !== ''
        ? String(item.accountUserId)
        : String(item.shopUserId ?? (item as any).id ?? ''),
      fullName: String(item.name || '').trim(),
      userName: String(item.name || '').trim(),
      role: String(item.roleName || item.role || '').trim(),
      phone: item.phone ? String(item.phone).trim() : '',
      email: item.email ? String(item.email).trim() : '',
      avatarUrl: item.avatarUrl ? String(item.avatarUrl).trim() : '',
      isActive: item.status === 'active' || (item.status as any) === 3,
    }));

    return { shopUsers, totalUser: total };
  };

  const shopUserList$ = memberStore && injector
    ? toObservable(computed(() => getShopUsers()), { injector }).pipe(
        shareReplay({ bufferSize: 1, refCount: true })
      )
    : of(getShopUsers());

  return {
    get currentUser() {
      return getUser();
    },
    user$: of(getUser()),
    shopUserList$,
  };
},
deps: [
  LocalStorage,
  AccountStore,
  [new Optional(), MemberStore],
  [new Optional(), Injector],
]
```

### 2.5. LƯU Ý KỸ THUẬT BẮT BUỘC TỪ SPEC GỐC (CRITICAL SPEC NOTES)
> **Trích xuất từ `docs/contexts/contexts.md:50-52` & `automation.md:59`**:
1. **Nguồn phát có Replay**: `shopUserList$` bắt buộc dùng nguồn có replay (`BehaviorSubject`, `ReplaySubject` hoặc `shareReplay({ bufferSize: 1, refCount: true })`), tuyệt đối cấm dùng `shopUserList$: of(null)` tĩnh vì remote MFE sẽ không bao giờ nhận được danh sách nhân viên.
2. **Phân biệt `null` và mảng rỗng `[]`**:
   - `null`: Trạng thái đang tải (pending) hoặc API gặp lỗi.
   - Mảng rỗng `{ shopUsers: [], totalUser: 0 }`: Đã tải xong hợp lệ nhưng cửa hàng không có nhân viên phụ. Không được đánh đồng hai trạng thái này.
3. **Phân biệt rõ ID nhân viên và ID tài khoản**:
   - `ShopUserDto.id`: ID bản ghi nhân viên trong cửa hàng.
   - `userId`: ID tài khoản người dùng (User ID). Giữ đúng kiểu và ý nghĩa từng trường, không dùng lẫn lộn.
4. **Quy chuẩn `totalUser`**:
   - Lấy giá trị tổng do backend trả về từ API, tuyệt đối không lấy `.length` của trang đầu tiên làm tổng nhân viên.
5. **Kiểm tra Shape dữ liệu**:
   - Generic `unknown` trong package `@wi-mfes/context` không chứng minh DTO đã đủ trường; bắt buộc kiểm tra shape khi ánh xạ response.
6. **Xác nhận nghiệp vụ trước khi đóng task**:
   - Đăng ký provider với trạng thái `null` chỉ hoàn thành phần DI. Phải kiểm tra dữ liệu được phát thực tế trước khi xác nhận màn hình/API hoạt động.
7. **Xử lý khi chưa có API**:
   - Giữ nguyên comment nợ kỹ thuật: `// chỗ này tạm thời để vậy -> có api thì thêm call api`.
   - Peer tuyệt đối không nhắm mắt chế endpoint giả; báo ngay cho Lead review lại task.

---

## 3. QUY TRÌNH PHẢN BIỆN PEER-TO-LEAD: "KHÔNG ĐƯỢC NHẮM MẮT MÀ LÀM"

> **NGUYÊN TẮC BẮT BUỘC**: Peer là kỹ sư chịu trách nhiệm thực thi trên mã nguồn, KHÔNG PHẢI robot paste code mù quáng. Khi nhận task, Peer BẮT BUỘC phải đọc và đối chiếu thực tế với codebase trước khi code.

```text
[Lead dispatch Task cho Peer]
             │
             ▼
   [Peer đọc Task & Codebase]
             │
      Có đúng thực tế?
      ├──► [ĐÚNG] ──► Peer tiến hành thi công code & Unit Test
      │
      └──► [KHÔNG ĐÚNG / BẤT THƯỜNG]
             │ (Phát hiện: thiếu API, lệch file, sai contract, nợ kỹ thuật)
             ▼
   [1. DỪNG THI CÔNG NGAY LẬP TỨC]
             │
             ▼
   [2. Chuyển Task sang BLOCKED trên Harness DB]
             │
             ▼
   [3. Báo cáo bằng chứng thực nghiệm cho Lead qua Orca/Terminal]
             │
             ▼
   [4. Lead rà soát lại kiến trúc (Lead Review Task)]
             │
      Kết quả xử lý của Lead:
      ├──► Điều chỉnh Task / Bổ sung Target Files & AC chuẩn
      ├──► Giữ nguyên Mock và cập nhật Spec nếu API chưa sẵn sàng
      └──► Đóng / Hủy task nếu yêu cầu phi thực tế
```

### 3.1. Các trường hợp Peer BẮT BUỘC dừng và báo cáo lại Lead
1. **Thiếu API hoặc API chưa sẵn sàng**:
   - Gặp comment `// chỗ này tạm thời để vậy -> có api thì thêm call api` mà Lead lại giao task yêu cầu xóa mock gọi API ngay mà không cung cấp URL/Swagger/DTO hợp lệ.
2. **Sai lệch thông tin định danh (Vague / Mismatched Task)**:
   - File mục tiêu không tồn tại, đường dẫn sai hoặc file đã bị refactor/rename.
   - Task thiếu 5 mục định danh theo chuẩn Zero-Search Task Specification.
3. **Xung đột kiểu dữ liệu hoặc Interface Contract**:
   - DTO của Lead mô tả không khớp với interface của thư viện `@wi-mfes/context`.
4. **Nguy cơ lỗi phụ trợ (Side-effects)**:
   - Sửa đổi gây gãy các remote MFEs khác (`mfe-crm`, `mfe-cdp`, `mfe-account`) hoặc gây vòng lặp tải mạng.

### 3.2. Cú pháp & Thao tác của Peer khi VETO / Báo cáo lại Lead
1. **Cập nhật Harness DB sang `Blocked`**:
   ```bash
   python3 tools/harness_manager.py update --id <task_id> --state Blocked
   ```
2. **Gửi báo cáo kèm bằng chứng thực nghiệm vào Terminal của Lead**:
   ```bash
   python3 -c '
   from tools.orca_slpc_bridge import find_live_terminal_for_role, send_to_terminal_safely
   lead_h = find_live_terminal_for_role("lead")
   msg = "[PHẢN BIỆN TỪ PEER -> LEAD]: Task #<task_id> có điểm bất thường: <Nêu rõ lý do & bằng chứng file:dòng>. Tạm dừng thi công, đề nghị Lead review lại task."
   send_to_terminal_safely(lead_h, msg)
   '
   ```
3. **Nếu Lead ép buộc làm sai**: Peer lập Bug P1 khiển trách Lead vi phạm `flawed_architecture`:
   ```bash
   python3 tools/agent_reprimand.py --from-role Peer --to-role Lead --violation flawed_architecture --task-id <id> --evidence "<bằng chứng>" --message "Yêu cầu thay mock bằng API khi backend chưa có endpoint" --penalize
   ```

### 3.3. Trách nhiệm của Lead khi nhận phản biện từ Peer
1. **Tiếp nhận & Không tự ái**: Lắng nghe phản hồi kỹ thuật khách quan từ Peer.
2. **Rà soát lại toàn diện**:
   - Khảo sát codebase và tài liệu nghiệp vụ qua `crm_doc_reader.py` hoặc hỏi User/Backend.
   - Nếu API chưa có: chỉ đạo Peer giữ nguyên mock, chuẩn hóa comment và đóng subtask.
   - Nếu có giải pháp thay thế: cập nhật lại description và dispatch lại task cho Peer.

---

## 4. MA TRẬN TIÊU CHÍ NGHIỆM THU (ACCEPTANCE CRITERIA MATRIX)

| Mã AC | Tiêu chí nghiệm thu | Phương pháp kiểm chứng | Kết quả kỳ vọng |
| :--- | :--- | :--- | :--- |
| **AC-SUL-01** | `WI_USER_CONTEXT` cung cấp đủ 3 thuộc tính `currentUser`, `user$`, `shopUserList$` | Unit Test Jest | Pass 100%, không thiếu thuộc tính nào trong contract |
| **AC-SUL-02** | `shopUserList$` duy trì an toàn dạng Observable | Unit Test RxJS | Phát ra `{ shopUsers: [], totalUser: 1 }` không crash |
| **AC-SUL-03** | Giữ comment hướng dẫn rõ ràng | Code Audit | Có comment `// chỗ này tạm thời để vậy -> có api thì thêm call api` |
| **AC-SUL-04** | Peer từ chối blind execution | Thẩm định quy trình | Peer dừng task và báo cáo Lead khi spec không đúng |
| **AC-SUL-05** | Lead rà soát lại task khi có phản hồi | Thẩm định quy trình | Task được cập nhật mô tả chính xác trước khi dispatch lại |

---

## 5. BÀN GIAO & LƯU TRỮ HỆ THỐNG
- Tài liệu này có hiệu lực ngay lập tức trên toàn bộ các phòng và terminal SLPC.
- Được lưu trữ chính thức tại:
  - `docs/spec/shop-user-list-context-spec.md`
  - `projects/wicx-crm-fe/docs/spec-shop-user-list-context.md`
