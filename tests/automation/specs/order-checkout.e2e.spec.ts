/**
 * Kịch Bản Kiểm Thử E2E Chuẩn Tester Team
 * Format: [ORDER_CHECKOUT_XXX]
 */
import { test, expect } from '@playwright/test';
import { OrderCheckoutPage } from '../pages/order-checkout.page';
import { ORDER_SMOKE_DATA } from '../data/order/checkout/order.smoke.data';
import { ORDER_VALIDATION_DATA } from '../data/order/checkout/order.validation.data';

test.describe('Order - Checkout Automation Suite', () => {
  let pageObj: OrderCheckoutPage;

  test.beforeEach(async ({ page }) => {
    pageObj = new OrderCheckoutPage(page);
    await pageObj.navigate();
  });

  test('[ORDER_CHECKOUT_001][@valid] Happy Path - Thao tác thành công', async ({ page }) => {
    await pageObj.searchInput.fill(ORDER_SMOKE_DATA.searchKeyword);
    await pageObj.submitButton.click();
    
    // Quy tắc @valid bắt buộc: verify lại trên danh sách sau action
    const row = pageObj.getRowItem(10293);
    await expect(row).toBeVisible();
  });

  test('[ORDER_CHECKOUT_002][@validate] Kiểm tra lỗi dữ liệu rỗng', async () => {
    await pageObj.searchInput.fill('');
    await pageObj.submitButton.click();
    await expect(pageObj.errorAlert).toBeVisible();
  });
});
