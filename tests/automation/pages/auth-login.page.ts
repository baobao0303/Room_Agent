/**
 * Page Object Model cho Màn hình Đăng nhập (Auth Login)
 * Tuân thủ 100% naming convention: auth-login-*
 * File: tests/automation/pages/auth-login.page.ts
 */

import { BasePage } from './base.page';

export class AuthLoginPage extends BasePage {
  // Locators theo contract bất biến
  public readonly loginForm = this.getByTestId('auth-login-form');
  public readonly usernameInput = this.getByTestId('auth-login-username-input');
  public readonly passwordInput = this.getByTestId('auth-login-password-input');
  public readonly submitButton = this.getByTestId('auth-login-submit-btn');
  public readonly submitButtonLoading = this.getByTestId('auth-login-submit-btn-loading');
  public readonly errorAlert = this.getByTestId('auth-login-error-alert');
  public readonly forgotPasswordLink = this.getByTestId('auth-forgot-password-link');

  public async navigate(): Promise<void> {
    await this.page.goto('/#/account/login');
    await this.loginForm.waitFor({ state: 'visible' });
  }

  public async login(username: string, password: string): Promise<void> {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  public async isErrorDisplayed(): Promise<boolean> {
    return await this.errorAlert.isVisible();
  }

  public async isLoading(): Promise<boolean> {
    return await this.submitButtonLoading.isVisible();
  }
}
