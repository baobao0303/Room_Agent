/**
 * Smoke Test Data (@valid, @integration, @e2e)
 */
import { OrderFactory } from './order.factory';

export const ORDER_SMOKE_DATA = {
  validPayload: OrderFactory.createDefault(),
  searchKeyword: 'Nguyen Van A',
};
