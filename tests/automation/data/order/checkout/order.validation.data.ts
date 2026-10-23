/**
 * Validation Test Data (@validate - Boundary / Negative / Empty / Required)
 */
export const ORDER_VALIDATION_DATA = {
  emptyName: { name: '' },
  exceedMaxLength: { name: 'A'.repeat(256) },
  specialCharacters: { name: '<script>alert(1)</script>' },
};
