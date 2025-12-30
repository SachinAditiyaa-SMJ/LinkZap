# LinkZap v0.1.0 - Initial Release 🚀

We're excited to announce the first release of **LinkZap**, a URL shortener service built with modern Python technologies. This is an early release with core functionality implemented.

## What is LinkZap?

LinkZap is a high-performance URL shortener service that converts long URLs into short, manageable links. Built with FastAPI, PostgreSQL, and Redis, it provides a simple REST API for creating, managing, and redirecting shortened URLs with optional expiration dates and status management.

## ✨ Key Features

### Core Functionality
- **🔗 URL Shortening**: Generate unique short codes using base62 encoding
- **⚡ Fast Redirects**: Efficient database lookups with proper indexing for optimal performance
- **🔄 Automatic Short Code Generation**: Redis-backed atomic counter ensures unique, sequential short codes
- **⏰ Expiration Management**: Optional expiration dates for temporary links
- **🎛️ Status Management**: Activate/deactivate URLs without deletion
- **🔍 Advanced Querying**: Filter URLs by ID, short code, or active status

### Technical Highlights
- **🚀 Fully Async Architecture**: Built with async/await throughout for maximum concurrency
- **📚 RESTful API**: Clean, well-documented API endpoints with automatic OpenAPI documentation
- **🐳 Docker Support**: Ready-to-use Docker container for easy deployment
- **📝 Structured Logging**: Comprehensive logging with Loguru

## 🛠️ Tech Stack

- **FastAPI** 0.128.0 - Modern, fast web framework
- **PostgreSQL** - Reliable relational database with async support (via asyncpg)
- **Redis** 7.1.0+ - In-memory data store for counter management
- **SQLAlchemy** 2.0.45 - Modern async ORM
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server
- **Loguru** - Structured logging

## 📡 API Endpoints

### Create Short URL
**POST** `/urls/shorten`
- Convert long URLs into short codes
- Optional expiration dates and status management

### Redirect to Original URL
**GET** `/urls/{short_code}`
- 307 redirects to original URLs
- Automatic expiration and status validation
- Proper HTTP status codes (307, 404, 410)
- ⚠️ Currently performs database lookup on each request (caching layer planned for future release)

### Get URL Information
**GET** `/urls/info/`
- Query URLs by ID, short code, or active status
- Flexible filtering options

### Update URL
**PUT** `/urls/{id}`
- Update original URL, expiration date, or active status
- Partial updates supported

## 🚀 Quick Start

### Prerequisites
- Python 3.14+
- PostgreSQL 12+
- Redis 6+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Install dependencies:**
```bash
uv sync
```

2. **Set environment variables:**
```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DATABASE=linkzap
export POSTGRES_USERNAME=postgres
export POSTGRES_PASSWORD=pass

export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0
```

3. **Run the application:**
```bash
uvicorn main:app --reload
```

### Docker Deployment

```bash
# Build image
docker build -t linkzap .

# Run container
docker run -d -p 8000:8000 --env-file .env linkzap
```

## 📖 Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🏗️ Architecture

LinkZap uses a solid foundation designed for future scalability:

- **Short Code Generation**: Redis atomic counter ensures unique sequential numbers, encoded in base62
- **Database Storage**: PostgreSQL with optimized indexes on `short_code` and `is_active`
- **Async Operations**: Fully asynchronous operations for maximum throughput
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes

**Note**: A caching layer for URL lookups is planned to improve redirect performance and reduce database load.

## 📦 What's Included

- Complete REST API implementation
- Database models with CRUD operations
- Request/response validation with Pydantic
- Redis-based short code generation
- Docker configuration
- Comprehensive logging
- API documentation

## ⚠️ Current Status & Known Limitations

This is an **early release** with core functionality. The following are included:
- Proper database indexing for performance
- Input validation and error handling
- Structured logging
- Docker containerization
- Environment-based configuration
- Async/await throughout for scalability

### Known Limitations

- **No caching layer**: Redirect lookups currently hit the database on every request, which may impact performance under high load
- **Not production-ready**: Additional optimizations and caching are required before production deployment

## 🗺️ Roadmap & Future Enhancements

### Planned for Next Release
- **🚀 Caching Layer**: Implement Redis caching for fast URL lookups to reduce database load
- **📊 Performance Optimization**: Add caching for frequently accessed short codes
- **🔍 Analytics**: URL access tracking and statistics
- **🔐 Rate Limiting**: API rate limiting for abuse prevention

### Future Considerations
- Custom short code support
- Bulk URL operations
- URL expiration cleanup jobs
- Enhanced monitoring and metrics

## 📝 Example Usage

```bash
# Create a short URL
curl -X POST "http://localhost:8000/urls/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://example.com/very/long/url",
    "expires_at": "2024-12-31T23:59:59Z",
    "is_active": true
  }'

# Redirect (use in browser or curl)
curl -L "http://localhost:8000/urls/a1b2c3d"

# Get URL info
curl "http://localhost:8000/urls/info/?short_code=a1b2c3d"
```

## 🎯 Use Cases

- Creating shareable links
- Tracking redirects
- Managing temporary URLs
- URL management systems
- Marketing campaigns with expiration dates

## 📄 License

See [LICENSE](LICENSE) file for details.

---

## 📋 Summary

This initial release provides the core URL shortening functionality with a solid foundation. While the service is functional and suitable for development/testing, **a caching layer is required before production deployment** to handle high-traffic redirects efficiently.

**Full Changelog**: This is the initial release of LinkZap v0.1.0

