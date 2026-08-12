from fastapi.testclient import TestClient

from rescued.app import PROCESSED_WEBHOOKS, app


client = TestClient(app)


def test_health_contract() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "1.0.0"}


def test_invoice_list_is_tenant_scoped_and_page_one_starts_at_first_item() -> None:
    response = client.get(
        "/api/invoices?page=1&page_size=2",
        headers={"X-Tenant-ID": "acme"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert [row["id"] for row in payload["items"]] == ["inv_1", "inv_3"]
    assert all(row["tenant"] == "acme" for row in payload["items"])


def test_cross_tenant_invoice_is_hidden_as_not_found() -> None:
    response = client.get("/api/invoices/inv_2", headers={"X-Tenant-ID": "acme"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Invoice not found"}


def test_missing_invoice_uses_404_not_500() -> None:
    response = client.get("/api/invoices/does-not-exist", headers={"X-Tenant-ID": "acme"})
    assert response.status_code == 404


def test_search_is_case_insensitive_and_tenant_scoped() -> None:
    response = client.get("/api/search?q=north", headers={"X-Tenant-ID": "acme"})
    assert response.status_code == 200
    assert [row["id"] for row in response.json()["items"]] == ["inv_1"]


def test_payment_webhook_is_idempotent() -> None:
    PROCESSED_WEBHOOKS.clear()
    headers = {"Idempotency-Key": "evt_123"}
    first = client.post("/api/webhooks/payment", headers=headers)
    retry = client.post("/api/webhooks/payment", headers=headers)

    assert first.json() == {"processed": True, "duplicate": False, "event_count": 1}
    assert retry.json() == {"processed": False, "duplicate": True, "event_count": 1}

