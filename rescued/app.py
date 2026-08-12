from fastapi import FastAPI, Header, HTTPException, Query


app = FastAPI(title="Invoice API — rescued")

INVOICES = [
    {"id": "inv_1", "tenant": "acme", "customer": "Northwind", "amount": 19.99},
    {"id": "inv_2", "tenant": "globex", "customer": "Umbrella", "amount": 250.00},
    {"id": "inv_3", "tenant": "acme", "customer": "Stark", "amount": 10.01},
]

PROCESSED_WEBHOOKS: set[str] = set()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/invoices")
def list_invoices(
    tenant_id: str = Header(alias="X-Tenant-ID"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=2, ge=1, le=100),
) -> dict:
    tenant_invoices = [row for row in INVOICES if row["tenant"] == tenant_id]
    start = (page - 1) * page_size
    return {
        "items": tenant_invoices[start : start + page_size],
        "total": len(tenant_invoices),
        "page": page,
        "page_size": page_size,
    }


@app.get("/api/invoices/{invoice_id}")
def get_invoice(invoice_id: str, tenant_id: str = Header(alias="X-Tenant-ID")) -> dict:
    for invoice in INVOICES:
        if invoice["id"] == invoice_id and invoice["tenant"] == tenant_id:
            return invoice
    raise HTTPException(status_code=404, detail="Invoice not found")


@app.get("/api/search")
def search(q: str, tenant_id: str = Header(alias="X-Tenant-ID")) -> dict:
    normalized_query = q.strip().casefold()
    return {
        "items": [
            row
            for row in INVOICES
            if row["tenant"] == tenant_id
            and normalized_query in row["customer"].casefold()
        ]
    }


@app.post("/api/webhooks/payment")
def payment_webhook(idempotency_key: str = Header(alias="Idempotency-Key")) -> dict:
    if idempotency_key in PROCESSED_WEBHOOKS:
        return {
            "processed": False,
            "duplicate": True,
            "event_count": len(PROCESSED_WEBHOOKS),
        }

    PROCESSED_WEBHOOKS.add(idempotency_key)
    return {
        "processed": True,
        "duplicate": False,
        "event_count": len(PROCESSED_WEBHOOKS),
    }

