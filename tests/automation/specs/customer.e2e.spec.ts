/**
 * Test Suite: Automation E2E Quản Lý Khách Hàng Chuẩn Tester Team
 * Format: [Module]_[Feature]_[Expected]_[Action]
 * File: tests/automation/specs/customer.e2e.spec.ts
 */

import { test, expect } from '@playwright/test';
import { CustomerListPage } from '../pages/customer-list.page';

test.describe('Phân Hệ Quản Lý Khách Hàng (Customer E2E Suite)', () => {
  let customerPage: CustomerListPage;

  test.beforeEach(async ({ page }) => {
    customerPage = new CustomerListPage(page);
    await customerPage.navigate('shop-demo-1');
  });

  test('[CUST_LIST_001][@query] [Customer]_[List]_[DisplayCorrectly]_[LoadPageWithEntityId]', async () => {
    // Kiểm tra bảng dữ liệu hiển thị
    await expect(customerPage.customerTable).toBeVisible();

    // Dòng dữ liệu bắt buộc phải có format: customer-row-{id} (Entity ID, không dùng index)
    const firstRow = customerPage.getCustomerRow(10293);
    await expect(firstRow).toBeVisible();
  });

  test('[CUST_SEARCH_002][@query] [Customer]_[Search]_[FilterByKeyword]_[SearchName]', async () => {
    await customerPage.searchCustomer('Nguyen Van A');

    // Verify kết quả tìm kiếm
    const matchedRow = customerPage.getCustomerRow(10293);
    await expect(matchedRow).toBeVisible();
  });

  test('[CUST_DELETE_003][@valid] [Customer]_[Delete]_[RemoveSuccess]_[ConfirmDeleteModal]', async () => {
    await customerPage.deleteCustomer(10293);

    // Xác nhận dòng khách hàng đã bị gỡ khỏi bảng
    const deletedRow = customerPage.getCustomerRow(10293);
    await expect(deletedRow).not.toBeVisible();

    // Quy tắc @valid: tìm kiếm lại để verify kết quả sau action
    await customerPage.searchCustomer('10293');
    await expect(deletedRow).not.toBeVisible();
  });

  test('[CUST_PAGING_004][@query] [Customer]_[Pagination]_[NextPageSuccess]_[ClickNextBtn]', async () => {
    await expect(customerPage.nextPaginationButton).toBeVisible();
    await customerPage.nextPaginationButton.click();

    // Verify bảng được refresh với tập dữ liệu trang mới
    await expect(customerPage.customerTable).toBeVisible();
  });
});
