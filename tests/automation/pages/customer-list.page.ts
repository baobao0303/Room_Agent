/**
 * Page Object Model cho Màn hình Danh sách Khách hàng (Customer List)
 * Tuân thủ 100% naming convention: customer-list-*, customer-row-*
 * File: tests/automation/pages/customer-list.page.ts
 */

import { BasePage } from './base.page';

export class CustomerListPage extends BasePage {
  public readonly customerTable = this.getByTestId('customer-list-table');
  public readonly searchInput = this.getByTestId('customer-list-search-input');
  public readonly filterButton = this.getByTestId('customer-list-filter-btn');
  public readonly exportButton = this.getByTestId('customer-list-export-btn');
  public readonly createButton = this.getByTestId('customer-list-create-btn');
  public readonly nextPaginationButton = this.getByTestId('customer-pagination-next-btn');

  // Modal xác nhận xóa
  public readonly deleteConfirmModal = this.getByTestId('customer-delete-confirm-modal');
  public readonly deleteConfirmPrimaryBtn = this.getByTestId('customer-delete-confirm-primary-btn');

  public async navigate(shopId = 'default'): Promise<void> {
    await this.page.goto(`/#/${shopId}/customers`);
    await this.customerTable.waitFor({ state: 'visible' });
  }

  public getCustomerRow(customerId: string | number) {
    return this.getDynamicTestId('customer-row', customerId);
  }

  public getDeleteButton(customerId: string | number) {
    return this.getDynamicTestId('customer-row-delete', customerId);
  }

  public async searchCustomer(keyword: string): Promise<void> {
    await this.searchInput.fill(keyword);
    await this.page.keyboard.press('Enter');
  }

  public async deleteCustomer(customerId: string | number): Promise<void> {
    const deleteBtn = this.getDeleteButton(customerId);
    await deleteBtn.click();
    await this.deleteConfirmModal.waitFor({ state: 'visible' });
    await this.deleteConfirmPrimaryBtn.click();
  }
}
