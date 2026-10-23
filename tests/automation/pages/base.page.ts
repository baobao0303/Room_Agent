/**
 * Lớp cơ sở BasePage cho toàn bộ Page Object Model
 * File: tests/automation/pages/base.page.ts
 */

import { getByTdsTestId, getDynamicTdsTestId, getTdsTestIdSelector } from '../helpers/qa-locator-helper';

export abstract class BasePage {
  constructor(protected page: any) {}

  /**
   * Helper locator bọc chuẩn tds-test-id
   */
  protected getByTestId(testId: string) {
    return getByTdsTestId(this.page, testId);
  }

  protected getDynamicTestId(prefix: string, entityId: string | number) {
    return getDynamicTdsTestId(this.page, prefix, entityId);
  }

  /**
   * Chờ phần tử xuất hiện trên DOM theo testId
   */
  public async waitForElement(testId: string, timeout = 5000): Promise<void> {
    await this.getByTestId(testId).waitFor({ state: 'visible', timeout });
  }

  /**
   * Kiểm tra phần tử có đang hiển thị hay không
   */
  public async isVisible(testId: string): Promise<boolean> {
    return await this.getByTestId(testId).isVisible();
  }
}
