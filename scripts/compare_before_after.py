from fastapi.testclient import TestClient

from before.app import PROCESSED_WEBHOOKS as BEFORE_EVENTS
from before.app import app as before_app
from rescued.app import PROCESSED_WEBHOOKS as AFTER_EVENTS
from rescued.app import app as rescued_app


def snapshot(client: TestClient, event_store: list | set) -> dict:
    event_store.clear()
    tenant_headers = {"X-Tenant-ID": "acme"}
    webhook_headers = {"Idempotency-Key": "evt_123"}

    health = client.get("/health").json()
    invoices = client.get(
        "/api/invoices?page=1&page_size=2", headers=tenant_headers
    ).json()
    forbidden = client.get("/api/invoices/inv_2", headers=tenant_headers)
    search = client.get("/api/search?q=north", headers=tenant_headers).json()
    first_webhook = client.post("/api/webhooks/payment", headers=webhook_headers).json()
    retried_webhook = client.post("/api/webhooks/payment", headers=webhook_headers).json()

    return {
        "health": health,
        "listed_invoice_ids": [row["id"] for row in invoices["items"]],
        "reported_total": invoices["total"],
        "cross_tenant_status": forbidden.status_code,
        "search_result_ids": [row["id"] for row in search["items"]],
        "first_webhook": first_webhook,
        "retried_webhook": retried_webhook,
    }


before = snapshot(TestClient(before_app), BEFORE_EVENTS)
after = snapshot(TestClient(rescued_app), AFTER_EVENTS)

print("BEFORE RESCUE")
for key, value in before.items():
    print(f"  {key}: {value}")

print("\nAFTER RESCUE")
for key, value in after.items():
    print(f"  {key}: {value}")

assert before != after
assert after["listed_invoice_ids"] == ["inv_1", "inv_3"]
assert after["reported_total"] == 2
assert after["cross_tenant_status"] == 404
assert after["search_result_ids"] == ["inv_1"]
assert after["retried_webhook"]["event_count"] == 1

print("\nRESCUE VERIFIED: all acceptance checks passed")

