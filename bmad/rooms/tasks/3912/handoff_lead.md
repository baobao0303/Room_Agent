# BIÊN BẢN BÀN GIAO CONTEXT (SLPC HANDOFF MEMO): Lead Dev ➔ Peer Dev 1

- **Thời gian**: `2026-10-21 16:15:00`
- **Work Item**: `#3912` (Bug nghiêm trọng: `#3921`)
- **Agent bàn giao (From)**: `Lead Dev`
- **Agent tiếp nhận (To)**: `Peer Dev 1` (`peer`)
- **Nội dung**: Sửa triệt để 3 lỗi kiến trúc theo Bug #3921: Dùng Employee DTO, xóa chuỗi || chắp vá, gỡ Optional MemberStore

---

## 1. Giao Việc Chuẩn 3 Phần & 5 Mục Bắt Buộc (5-Point Mandatory Specification)

### 1.1. Target Files (Single-Ownership)
- `apps/app-shell/src/app/pages/setting/provider/context.provider.ts`
- `apps/app-shell/src/app/pages/setting/provider/context.provider.spec.ts`

### 1.2. Anchors / Lines
- `apps/app-shell/src/app/pages/setting/provider/context.provider.ts`: Dòng 130-185 tại `provide: WI_USER_CONTEXT`.
- `apps/app-shell/src/app/pages/setting/provider/context.provider.spec.ts`: Test suite cho `MemberStore`.

### 1.3. Concrete Changes (3 Điểm Sửa Bắt Buộc Theo Bug #3921)
1. **Dùng DTO `Employee` thay vì `any`**:
   - Import `Employee` từ `@wicx/features/member`.
   - Trong mapping: `list.map((emp: Employee) => ...)` — TUYỆT ĐỐI CẤM `(emp: any)`.
2. **Xóa sạch chuỗi `||` fallback chắp vá vô căn cứ**:
   - `id`: `emp.shopUserId`
   - `userId`: `emp.accountUserId ? String(emp.accountUserId) : String(emp.shopUserId)`
   - `fullName`: `emp.name`
   - `userName`: `emp.name`
   - `role`: `emp.roleName ?? emp.role ?? ''`
   - `phone`: `emp.phone`
   - `email`: `emp.email ?? ''`
   - `avatarUrl`: `emp.avatarUrl ?? ''`
   - `isActive`: `emp.status === '3' || emp.status === 'active' || emp.status === 'working'`
3. **Gỡ bỏ `new Optional()` ở `MemberStore`**:
   - `MemberStore` là core root store của member domain, inject trực tiếp:
     ```typescript
     useFactory: (
       storage: LocalStorage,
       accountStore: InstanceType<typeof AccountStore>,
       memberStore: InstanceType<typeof MemberStore>,
       eventBus?: EventBusService | null
     ): WIUserContext<any> => { ... }
     deps: [
       LocalStorage,
       AccountStore,
       MemberStore,
       [new Optional(), EventBusService],
     ]
     ```
4. Trong `context.provider.spec.ts`:
   - Đảm bảo mock `MemberStore` cung cấp mảng `Employee[]` chuẩn kiểu dữ liệu.

### 1.4. Acceptance Criteria
- **AC-01**: 0% `any` trong mapping `list.map((emp: Employee) => ...)`.
- **AC-02**: Không còn chuỗi `||` fallback chắp vá (`emp.name || emp.displayName`, etc.).
- **AC-03**: `MemberStore` được inject trực tiếp không qua `new Optional()`.
- **AC-04**: `npx nx test app-shell --testFile=context.provider.spec.ts` pass 100%.

### 1.5. Test Command
```bash
npx nx test app-shell --testFile=context.provider.spec.ts
```
