from fastapi import FastAPI, HTTPException
from mangum import Mangum

from app.database import create_tables
from app.schemas import OrderCreate
from app.service import ExchangeService

app = FastAPI(
    title="Cloud Exchange Engine",
    description="A beginner-friendly REST API for a limit-order exchange engine.",
    version="1.0.0",
)

service = ExchangeService()


@app.on_event("startup")
def startup():
    create_tables()


@app.get("/")
def home():
    return {
        "service": "Cloud Exchange Engine",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health():
    return {"status": "UP", "service": "cloud-exchange-engine"}


@app.post("/api/orders", status_code=201)
def create_order(request: OrderCreate):
    try:
        return service.place_order(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/orders/{order_id}")
def get_order(order_id: int):
    order = service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.delete("/api/orders/{order_id}")
def cancel_order(order_id: int):
    try:
        cancelled = service.cancel_order(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not cancelled:
        raise HTTPException(status_code=400, detail="Order cannot be cancelled or is already filled")
    return {"cancelled": True, "order_id": order_id}


@app.get("/api/orderbook/{symbol}")
def get_orderbook(symbol: str):
    return service.get_orderbook(symbol.upper())


@app.get("/api/trades/{symbol}")
def get_trades(symbol: str):
    return service.get_trades(symbol.upper())


handler = Mangum(app)
