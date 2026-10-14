# Technical Architecture & Dev Spec: Example Project

## 1. Technical Stack
- **Framework**: Angular 18+ (Standalone Components, Signals)
- **UI Library**: `tds-ui`
- **State Management**: Angular Signals / RxJS

## 2. API Contract & DTOs

```typescript
export interface UserDto {
  id: string;
  fullName: string;
  email: string;
  role: 'admin' | 'editor' | 'viewer';
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface UserListQueryDto {
  page: number;
  pageSize: number;
  search?: string;
  status?: string;
  role?: string;
}

export interface PaginatedResultDto<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}
```

## 3. Component Architecture
- `UserListComponent` (`projects/example-project/src/app/features/users/user-list.component.ts`)
- `UserService` (`projects/example-project/src/app/core/services/user.service.ts`)
