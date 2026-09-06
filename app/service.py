from sqlalchemy import select

from app.database import SessionLocal
from app.models import Order, Trade
from app.schemas import OrderCreate, Side


class ExchangeService:
    """Simple limit-order matching service using price-time priority."""

    def place_order(self, request: OrderCreate):
        symbol = request.symbol.upper()

        with SessionLocal() as session:
            incoming = Order(
                user_id=request.user_id,
                symbol=symbol,
                side=request.side.value,
                price=request.price,
                original_quantity=request.quantity,
                remaining_quantity=request.quantity,
                status="OPEN",
            )
            session.add(incoming)
            session.flush()

            opposite = "SELL" if request.side == Side.BUY else "BUY"

            if request.side == Side.BUY:
                stmt = (
                    select(Order)
                    .where(
                        Order.symbol == symbol,
                        Order.side == opposite,
                        Order.status.in_(["OPEN", "PARTIALLY_FILLED"]),
                        Order.remaining_quantity > 0,
                        Order.price <= request.price,
                    )
                    .order_by(Order.price.asc(), Order.id.asc())
                    .with_for_update()
                )
            else:
                stmt = (
                    select(Order)
                    .where(
                        Order.symbol == symbol,
                        Order.side == opposite,
                        Order.status.in_(["OPEN", "PARTIALLY_FILLED"]),
                        Order.remaining_quantity > 0,
                        Order.price >= request.price,
                    )
                    .order_by(Order.price.desc(), Order.id.asc())
                    .with_for_update()
                )

            for resting in session.execute(stmt).scalars().all():
                if incoming.remaining_quantity <= 0:
                    break

                matched = min(
                    incoming.remaining_quantity,
                    resting.remaining_quantity,
                )
                execution_price = resting.price

                incoming.remaining_quantity -= matched
                resting.remaining_quantity -= matched

                incoming.status = (
                    "FILLED"
                    if incoming.remaining_quantity <= 1e-9
                    else "PARTIALLY_FILLED"
                )
                resting.status = (
                    "FILLED"
                    if resting.remaining_quantity <= 1e-9
                    else "PARTIALLY_FILLED"
                )

                session.add(
                    Trade(
                        buy_order_id=incoming.id if incoming.side == "BUY" else resting.id,
                        sell_order_id=incoming.id if incoming.side == "SELL" else resting.id,
                        symbol=symbol,
                        price=execution_price,
                        quantity=matched,
                    )
                )

            if incoming.remaining_quantity > 1e-9:
                incoming.status = (
                    "PARTIALLY_FILLED"
                    if incoming.remaining_quantity < incoming.original_quantity
                    else "OPEN"
                )

            session.commit()
            session.refresh(incoming)
            return self._order_dict(incoming)

    def get_order(self, order_id: int):
        with SessionLocal() as session:
            order = session.get(Order, order_id)
            return self._order_dict(order) if order else None

    def cancel_order(self, order_id: int):
        with SessionLocal() as session:
            order = session.get(Order, order_id)
            if order is None:
                raise ValueError("Order not found")
            if order.status in ("FILLED", "CANCELLED"):
                return False
            order.status = "CANCELLED"
            session.commit()
            return True

    def get_orderbook(self, symbol: str):
        with SessionLocal() as session:
            orders = session.execute(
                select(Order).where(
                    Order.symbol == symbol,
                    Order.status.in_(["OPEN", "PARTIALLY_FILLED"]),
                    Order.remaining_quantity > 0,
                )
            ).scalars().all()

            buys = sorted(
                [o for o in orders if o.side == "BUY"],
                key=lambda o: (-o.price, o.id),
            )
            sells = sorted(
                [o for o in orders if o.side == "SELL"],
                key=lambda o: (o.price, o.id),
            )

            return {
                "symbol": symbol,
                "buy_orders": [self._order_dict(o) for o in buys],
                "sell_orders": [self._order_dict(o) for o in sells],
            }

    def get_trades(self, symbol: str):
        with SessionLocal() as session:
            rows = session.execute(
                select(Trade)
                .where(Trade.symbol == symbol)
                .order_by(Trade.id.asc())
            ).scalars().all()
            return [self._trade_dict(t) for t in rows]

    @staticmethod
    def _order_dict(order: Order):
        return {
            "id": order.id,
            "user_id": order.user_id,
            "symbol": order.symbol,
            "side": order.side,
            "price": order.price,
            "original_quantity": order.original_quantity,
            "remaining_quantity": order.remaining_quantity,
            "status": order.status,
            "created_at": order.created_at,
        }

    @staticmethod
    def _trade_dict(trade: Trade):
        return {
            "id": trade.id,
            "buy_order_id": trade.buy_order_id,
            "sell_order_id": trade.sell_order_id,
            "symbol": trade.symbol,
            "price": trade.price,
            "quantity": trade.quantity,
            "created_at": trade.created_at,
        }
