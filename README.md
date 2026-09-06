# Cloud Exchange Engine

Beginner-friendly cloud exchange order matching engine using Python, FastAPI, PostgreSQL, and Vercel.

## Features
- Limit BUY/SELL orders
- Price-time priority
- Partial fills
- Cancellation
- PostgreSQL persistence
- REST API and Swagger
- Vercel serverless deployment
- GitHub Actions CI and unit tests

## Endpoints
- `GET /`
- `GET /api/health`
- `POST /api/orders`
- `GET /api/orders/{id}`
- `DELETE /api/orders/{id}`
- `GET /api/orderbook/{symbol}`
- `GET /api/trades/{symbol}`
- `GET /docs`

## Deployment
Add the Neon PostgreSQL connection string as the Vercel environment variable `DATABASE_URL`. Never commit the real connection string.
