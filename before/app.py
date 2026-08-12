from fastapi import FastAPI, Header, HTTPException, Query


app = FastAPI(title="Invoice API — before rescue")

INVOICES = [
    {"id": "inv_1", "tenant": "acme", "customer": "Northwind", "amount": 19.99},
    {"id": "inv_2", "tenant": "globex", "customer": "Umbrella", "amount": 250.00},
    {"id": "inv_3", "tenant": "acme", "customer": "Stark", "amount": 10.01},
]

PROCESSED_WEBHOOKS: list[str] = []


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/invoices")
def list_invoices(
    tenant_id: str = Header(alias="X-Tenant-ID"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=2, ge=1, le=100),
) -> dict:
    # BUG: tenant_id is ignored, leaking other customers' invoices.
    # BUG: page 1 starts at page_size instead of zero.
    start = page * page_size
    return {"items": INVOICES[start : start + page_size], "total": len(INVOICES)}


@app.get("/api/invoices/{invoice_id}")
def get_invoice(invoice_id: str, tenant_id: str = Header(alias="X-Tenant-ID")) -> dict:
    for invoice in INVOICES:
        if invoice["id"] == invoice_id:
            # BUG: no ownership check.
            return invoice
    raise HTTPException(status_code=500, detail="Invoice lookup failed")


@app.get("/api/search")
def search(q: str) -> dict:
    # BUG: search is unexpectedly case-sensitive.
    return {"items": [row for row in INVOICES if q in row["customer"]]}


@app.post("/api/webhooks/payment")
def payment_webhook(idempotency_key: str = Header(alias="Idempotency-Key")) -> dict:
    # BUG: retries create duplicate side effects.
    PROCESSED_WEBHOOKS.append(idempotency_key)
    return {"processed": True, "event_count": len(PROCESSED_WEBHOOKS)}

