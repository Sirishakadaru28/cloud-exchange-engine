import os
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.database as database
from app.database import Base
from app.service import ExchangeService
from app.schemas import OrderCreate, Side


def setup_database():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    database.engine = engine
    database.SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def test_matching():
    setup_database()
    service = ExchangeService()

    buy = service.place_order(
        OrderCreate(user_id=1, symbol="BTC-USD", side=Side.BUY, price=100, quantity=2)
    )
    sell = service.place_order(
        OrderCreate(user_id=2, symbol="BTC-USD", side=Side.SELL, price=100, quantity=1)
    )

    assert buy["status"] == "PARTIALLY_FILLED"
    assert sell["status"] == "FILLED"
    assert buy["remaining_quantity"] == 1

    trades = service.get_trades("BTC-USD")
    assert len(trades) == 1
    assert trades[0]["price"] == 100


def test_price_priority():
    setup_database()
    service = ExchangeService()

    first = service.place_order(
        OrderCreate(user_id=1, symbol="BTC-USD", side=Side.BUY, price=100, quantity=1)
    )
    better = service.place_order(
        OrderCreate(user_id=2, symbol="BTC-USD", side=Side.BUY, price=101, quantity=1)
    )
    service.place_order(
        OrderCreate(user_id=3, symbol="BTC-USD", side=Side.SELL, price=100, quantity=1)
    )

    trades = service.get_trades("BTC-USD")
    assert trades[0]["buy_order_id"] == better["id"]
    assert first["id"] != better["id"]


def test_cancel():
    setup_database()
    service = ExchangeService()

    order = service.place_order(
        OrderCreate(user_id=1, symbol="ETH-USD", side=Side.BUY, price=200, quantity=1)
    )
    assert service.cancel_order(order["id"]) is True
    assert service.get_order(order["id"])["status"] == "CANCELLED"
