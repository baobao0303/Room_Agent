/**
 * QA Automation Locator Helper for TDS Test ID Design Guideline
 * File: tests/automation/helpers/qa-locator-helper.ts
 */

export interface LocatorContext {
  locator: (selector: string) => any;
}

/**
 * Trả về chuỗi CSS selector chuẩn cho TDS Test ID
 */
export const getTdsTestIdSelector = (testId: string): string => `[tds-test-id="${testId}"]`;

/**
 * Tìm phần tử DOM dựa trên tds-test-id cố định
 */
export const getByTdsTestId = <T extends LocatorContext>(context: T, testId: string) => {
  return context.locator(getTdsTestIdSelector(testId));
};

/**
 * Tìm phần tử DOM động dựa trên tiền tố và ID thực thể nghiệp vụ (Entity ID)
 * Ví dụ: getDynamicTdsTestId(page, 'customer-row', 10293) -> [tds-test-id="customer-row-10293"]
 */
export const getDynamicTdsTestId = <T extends LocatorContext>(
  context: T,
  prefix: string,
  entityId: string | number
) => {
  return context.locator(getTdsTestIdSelector(`${prefix}-${entityId}`));
};
