# LinkZap

A fast, production-ready URL shortener service built with FastAPI, PostgreSQL, and Redis. LinkZap provides a simple REST API to convert long URLs into short, manageable links with optional expiration dates and status management. Perfect for creating shareable links, tracking redirects, and managing temporary URLs.

## Features

- **URL Shortening**: Generate unique short codes using base62 encoding
- **Automatic Short Code Generation**: Redis-backed counter ensures unique, sequential short codes
- **Expiration Management**: Optional expiration dates for temporary links
- **Status Management**: Activate/deactivate URLs without deletion
- **Fast Redirects**: Efficient database lookups with proper indexing
- **Async Architecture**: Fully asynchronous FastAPI with async PostgreSQL and Redis
- **RESTful API**: Clean, well-documented API endpoints
- **Filtering & Querying**: Query URLs by ID, short code, or active status

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Reliable relational database with async support (via asyncpg)
- **Redis**: In-memory data store for counter management
- **SQLAlchemy 2.0**: Modern async ORM
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server
- **Loguru**: Structured logging

## Installation

### Prerequisites

- Python 3.14+
- PostgreSQL 12+
- Redis 6+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. **Install dependencies:**
```bash
uv sync
```

2. **Set environment variables:**

Create a `.env` file or export the following variables:

```bash
# PostgreSQL Configuration
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DATABASE=linkzap
export POSTGRES_USERNAME=postgres
export POSTGRES_PASSWORD=pass

# Redis Configuration
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0
```

## Running

### Development

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Create Short URL

**POST** `/urls/shorten`

Create a new short URL from a long URL.

**Request Body:**
```json
{
  "original_url": "https://example.com/very/long/url",
  "expires_at": "2024-12-31T23:59:59Z",  // Optional
  "is_active": true  // Optional, defaults to true
}
```

**Response:**
```json
{
  "id": 1,
  "short_code": "a1b2c3d",
  "original_url": "https://example.com/very/long/url",
  "expires_at": "2024-12-31T23:59:59Z",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Redirect to Original URL

**GET** `/urls/{short_code}`

Redirects to the original URL associated with the short code.

- Returns `307 Temporary Redirect` if URL is active and not expired
- Returns `404 Not Found` if URL doesn't exist or is inactive
- Returns `410 Gone` if URL has expired

### Get URL Information

**GET** `/urls/info/?id={id}&short_code={code}&is_active={true|false}`

Retrieve URL details by filtering with query parameters.

**Query Parameters:**
- `id` (optional): Database primary key
- `short_code` (optional): Short code of the URL
- `is_active` (optional): Filter by active status

**Response:**
```json
[
  {
    "id": 1,
    "short_code": "a1b2c3d",
    "original_url": "https://example.com/very/long/url",
    "expires_at": "2024-12-31T23:59:59Z",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### Update URL

**PUT** `/urls/{id}`

Update an existing URL's properties.

**Request Body:**
```json
{
  "original_url": "https://new-url.com",  // Optional
  "expires_at": "2025-12-31T23:59:59Z",   // Optional
  "is_active": false  // Optional
}
```

**Response:**
```json
{
  "id": 1,
  "short_code": "a1b2c3d",
  "original_url": "https://new-url.com",
  "expires_at": "2025-12-31T23:59:59Z",
  "is_active": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T01:00:00Z"
}
```

## Docker

### Build Image

```bash
docker build -t linkzap .
```

### Run Container

```bash
docker run -d -p 8000:8000 --env-file .env linkzap
```

Make sure your `.env` file contains all required environment variables (PostgreSQL and Redis configuration).

## Project Structure

```
LinkZap/
├── app/
│   ├── api/           # API routes and endpoints
│   ├── models/        # SQLAlchemy database models
│   ├── schemas/       # Pydantic request/response schemas
│   ├── services/      # Database and Redis service layers
│   └── utils/         # Utility functions (shortcode generation)
├── main.py            # FastAPI application entry point
├── pyproject.toml     # Project dependencies and configuration
└── Dockerfile         # Docker container configuration
```

## How It Works

1. **Short Code Generation**: Uses a Redis counter that increments atomically, ensuring unique sequential numbers. These numbers are then encoded in base62 to create short, URL-friendly codes.

2. **Database Storage**: URLs are stored in PostgreSQL with indexes on `short_code` and `is_active` for fast lookups.

3. **Redirect Flow**: When a short code is accessed, the system:
   - Looks up the URL in the database
   - Checks if it's active
   - Validates expiration date (if set)
   - Performs a 307 redirect to the original URL

## License

See LICENSE file.