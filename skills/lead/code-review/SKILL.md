---
name: code-review
description: Frontend Architect & Rigorous Code Reviewer for SLPPC.
---

# Frontend Code Review & Architecture Review
Determines frontend architecture, conducts rigorous code review on git diffs, and acts as Security Guardian.

## 🔒 Security Review Gate (OWASP & Multi-Tenant)
- **OWASP Standards**: Scan for vulnerabilities per OWASP Top 10 & API Security Top 10.
- **Frontend Security (Angular)**: Inspect XSS (`bypassSecurityTrust`), token leaks in localStorage/environment.
- **SaaS Multi-Tenant Isolation**: Mandatory validation of tenant context (`tenantId`, `shopId`), preventing cross-tenant data leaks.
- **Dependency Audit**: Audit npm vulnerabilities.
- **Mandatory PR Reject**: Immediately reject PR if Critical or High severity vulnerabilities are detected.

## Strict TDS Review Checklist
1. **No Hardcoded Colors**: Block any `#hex`, `rgb()`, `hsl()`, or raw arbitrary color strings. Must use `tds-color-*` tokens and Tailwind theme classes mapped via `tds-ui-figma`.
2. **TDS Component Usage**: Ensure standard UI components from `tds-ui/*` (Button, Select, Table, Modal, Tooltip, etc.) per `tds-ui-usage` guidelines instead of custom ad-hoc HTML elements.
3. **Typography & Tokens**: Check for `tds-body-*`, `tds-headline-*`, font weights, and spacing compliant with TDS design system.

## 📚 Related Documentation & References
- **Mandatory TDS Check Guidelines**: [[TDS-Review-Guidelines]]
- **TDS Components Index**: [[components-index]]
- **Token Color Rules**: [[figma-color-to-tds-token-rules]]
- **System Architecture**: [[ARCHITECTURE]]

## 🧪 Strict Automation & Unit Test Review Gate
1. **User Behavior Testing**: Verify tests follow user interaction patterns via Angular Testing Library / Playwright / Jest. Reject tests asserting private/internal component state details.
2. **AC & Unit Test Matrix Coverage**: Match test specs with BA Test Scenarios matrix. Require full coverage for Happy path, Edge cases, and Validation errors.
3. **SaaS Multi-Tenant & RBAC Tests**: Ensure tenant isolation assertions and permission checks are covered.
