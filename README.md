# LinkZap

A fast URL shortener service built with FastAPI and PostgreSQL. LinkZap provides a simple REST API to convert long URLs into short, manageable links with optional expiration dates and status management. Perfect for creating shareable links, tracking redirects, and managing temporary URLs.

## Features

- URL shortening with short codes
- Optional expiration dates
- Active/inactive status management
- Async FastAPI with PostgreSQL

## Installation

1. Install dependencies:
```bash
uv sync
```

2. Set environment variables:
```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DATABASE=linkzap
export POSTGRES_USERNAME=postgres
export POSTGRES_PASSWORD=pass
```

## Running

```bash
uvicorn main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Docker

```bash
docker build -t linkzap .
docker run -d -p 8000:8000 --env-file .env linkzap
```

## License

See LICENSE file.