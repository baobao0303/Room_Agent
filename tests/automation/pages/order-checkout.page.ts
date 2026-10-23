/**
 * Page Object Model cho Order Checkout
 * Tuân thủ 100% naming convention: order-checkout-*
 */
import { getByTdsTestId, getDynamicTdsTestId } from '../helpers/qa-locator-helper';

export class OrderCheckoutPage {
  constructor(private page: any) {}

  // Locators độc quyền qua tds-test-id
  public readonly mainContainer = getByTdsTestId(this.page, 'order-checkout-container');
  public readonly searchInput = getByTdsTestId(this.page, 'order-checkout-search-input');
  public readonly submitButton = getByTdsTestId(this.page, 'order-checkout-submit-btn');
  public readonly errorAlert = getByTdsTestId(this.page, 'order-checkout-error-alert');

  public getRowItem(entityId: string | number) {
    return getDynamicTdsTestId(this.page, 'order-row', entityId);
  }

  public async navigate(): Promise<void> {
    await this.page.goto('/#/order/checkout');
    await this.mainContainer.waitFor({ state: 'visible' });
  }
}
