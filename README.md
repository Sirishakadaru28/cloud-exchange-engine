# Cloud Exchange Engine

A beginner-friendly exchange order matching engine built with **Python, FastAPI, PostgreSQL and Vercel**.

This is an independent educational implementation inspired by the general concept of exchange matching engines. It is **not a copy or fork of exchange-core**.

## Features

- Limit BUY and SELL orders
- Price-time priority
- Partial fills
- Order cancellation
- Persistent PostgreSQL storage
- REST API with FastAPI
- Swagger/OpenAPI documentation
- Health endpoint
- Unit tests
- GitHub Actions CI
- Vercel serverless deployment

## Architecture

Client -> Vercel -> FastAPI -> Matching Engine -> PostgreSQL

## API

- `GET /api/health`
- `POST /api/orders`
- `GET /api/orders/{id}`
- `DELETE /api/orders/{id}`
- `GET /api/orderbook/{symbol}`
- `GET /api/trades/{symbol}`

After deployment, open `/docs` on your Vercel domain for interactive API testing.

## Deployment

1. Create a PostgreSQL database using a managed provider such as Neon or Supabase.
2. Copy its PostgreSQL connection string.
3. Push this repository to GitHub.
4. Import the repository into Vercel.
5. Add the Vercel environment variable `DATABASE_URL`.
6. Deploy.
7. Open `https://YOUR-DOMAIN.vercel.app/docs`.

Never commit database passwords or secrets.

## Example

POST `/api/orders`

```json
{
  "user_id": 1,
  "symbol": "BTC-USD",
  "side": "BUY",
  "price": 100,
  "quantity": 2
}
```

Then create a SELL order at 100. The engine creates a trade for the matching quantity.

## Local development

Python 3.11+:

```bash
python -m venv .venv
pip install -r requirements.txt
uvicorn api.index:app --reload
```

A PostgreSQL `DATABASE_URL` is required.

## Limitations

This is a learning/demo exchange, not a real financial trading platform. It does not implement authentication, real-money settlement, distributed locking, regulatory controls, or high-frequency production performance.

## Future improvements

- JWT authentication
- WebSocket market data
- Redis coordination
- Alembic migrations
- Docker
- Azure deployment
- metrics and monitoring
- integration tests
- frontend trading dashboard
