/**
 * Test Data Factory cho Module: Order
 * Tuân thủ chuẩn Outline: RULE: PATTERN FILE DATA TEST
 */

export interface OrderPayload {
  id?: number;
  code: string;
  name: string;
  status: string;
}

export class OrderFactory {
  public static createDefault(override: Partial<OrderPayload> = {}): OrderPayload {
    const rand = Math.floor(Math.random() * 89999) + 10000;
    return {
      code: `ORDER_${rand}`,
      name: `Khách hàng Tự động ${rand}`,
      status: 'active',
      ...override,
    };
  }
}
