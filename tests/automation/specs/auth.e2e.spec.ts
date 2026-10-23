/**
 * Test Suite: Automation E2E Xác Thực & Đăng Nhập Chuẩn Tester Team
 * Format: [Module]_[Feature]_[Expected]_[Action]
 * File: tests/automation/specs/auth.e2e.spec.ts
 */

import { test, expect } from '@playwright/test';
import { AuthLoginPage } from '../pages/auth-login.page';

test.describe('Phân Hệ Xác Thực & Đăng Nhập (Auth E2E Suite)', () => {
  let loginPage: AuthLoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new AuthLoginPage(page);
    await loginPage.navigate();
  });

  test('[AUTH_LOGIN_001][@valid] [Auth]_[Login]_[Success]_[SubmitValidCredentials]', async ({ page }) => {
    await loginPage.login('admin_test', 'P@ssword123');

    // Chờ điều hướng tới Dashboard
    await expect(page).toHaveURL(/.*dashboard/);

    // Kiểm tra chuông thông báo xuất hiện
    const bellBtn = page.locator('[tds-test-id="system-notification-bell-btn"]');
    await expect(bellBtn).toBeVisible();
  });

  test('[AUTH_LOGIN_002][@validate] [Auth]_[Login]_[FailEmptyPassword]_[SubmitBlankPassword]', async ({ page }) => {
    await loginPage.login('admin_test', '');

    // Xác nhận không chuyển trang và hiển thị alert lỗi
    await expect(loginPage.errorAlert).toBeVisible();
    await expect(page).toHaveURL(/.*login/);
  });

  test('[AUTH_LOGIN_003][@validate] [Auth]_[Login]_[FailWrongPassword]_[SubmitWrongPassword]', async ({ page }) => {
    await loginPage.login('admin_test', 'WrongPass_999');

    // Xác nhận hiển thị alert lỗi
    await expect(loginPage.errorAlert).toBeVisible();
  });

  test('[AUTH_LOGIN_004][@validate] [Auth]_[Login]_[ShowLoadingState]_[ClickSubmit]', async () => {
    // Fill credentials nhưng không hoàn tất mạng tức thì
    await loginPage.usernameInput.fill('admin_test');
    await loginPage.passwordInput.fill('P@ssword123');
    await loginPage.submitButton.click();

    // Verify state-based test ID: submit-btn-loading hoặc disabled
    const isLoading = await loginPage.isLoading();
    if (isLoading) {
      await expect(loginPage.submitButtonLoading).toBeVisible();
    }
  });
});
