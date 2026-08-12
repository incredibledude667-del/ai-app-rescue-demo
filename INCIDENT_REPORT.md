# Invoice API rescue report

## Scope

Repair a small AI-generated FastAPI service using a fixed acceptance contract. The rescue keeps the public endpoints but fixes data isolation, pagination, response semantics, search, and webhook retries.

## Confirmed defects and fixes

| Defect | User impact | Fix | Regression evidence |
| --- | --- | --- | --- |
| Invoice list ignored tenant | Cross-customer data exposure | Filter before pagination | `test_invoice_list_is_tenant_scoped...` |
| Page 1 skipped first records | Missing results | Zero-based offset `(page - 1) * page_size` | Same test |
| Invoice lookup ignored owner | Cross-tenant read | Match invoice and tenant together | `test_cross_tenant_invoice...` |
| Missing invoice returned 500 | False server incident | Stable 404 contract | `test_missing_invoice_uses_404...` |
| Search was case-sensitive and global | Expected records missing; leakage | Normalize query and scope to tenant | `test_search_is_case_insensitive...` |
| Payment retry duplicated side effect | Duplicate processing | Idempotency set with duplicate response | `test_payment_webhook_is_idempotent` |

## Definition of done

- Six acceptance tests pass.
- The before/after comparison demonstrates every changed contract.
- The API can be run locally with Uvicorn.
- No production credentials or customer data are used.

## Commands

```bash
python -m pytest -q
python -m scripts.compare_before_after
uvicorn rescued.app:app --reload
```
