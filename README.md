# Statishub Company API

> FastAPI-based REST API providing Vietnamese company data from business registries

[![CI/CD Pipeline](https://github.com/yourusername/statishub/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/statishub/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.127.0-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- 🏢 **Company Data**: Organization profiles, financial statements, shareholder information
- 🔍 **Search**: Full-text search across company database
- 🔐 **API Key Authentication**: Secure access with credit-based usage
- ⚡ **Redis Caching**: Fast response times with intelligent caching
- 📊 **Health Monitoring**: Built-in health check endpoints
- 🐳 **Docker Ready**: Production-ready containerization
- 📝 **OpenAPI Docs**: Auto-generated API documentation
- 🧪 **Well Tested**: Comprehensive test coverage

## Quick Start

### Prerequisites

- Python 3.11+
- Redis 7+
- Supabase account (or PostgreSQL database)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/statishub.git
   cd statishub
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Admin UI: http://localhost:8000/admin-ui/login

### Using Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## API Endpoints

### Company Data

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/company/{taxcode}` | GET | Get company profile | API Key |
| `/company/{taxcode}/balance-sheet` | GET | Get balance sheets | API Key |
| `/company/{taxcode}/income-statement` | GET | Get income statements | API Key |
| `/company/{taxcode}/cashflow` | GET | Get cash flow statements | API Key |
| `/company/{taxcode}/shareholders` | GET | Get shareholder information | API Key |
| `/company/{taxcode}/personnel` | GET | Get key personnel | API Key |
| `/company/{taxcode}/compliance` | GET | Get compliance data | API Key |
| `/search?name={query}` | GET | Search companies | API Key |

### Health Checks

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/health` | GET | Basic health check | None |
| `/health/redis` | GET | Redis connection status | None |
| `/health/database` | GET | Database connection status | None |

### Admin

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/admin/api-keys/` | POST | Create API key | Admin Key |
| `/admin/api-keys/` | GET | List API keys | Admin Key |
| `/admin/api-keys/{key}/credit` | POST | Add credits | Admin Key |
| `/admin/api-keys/{key}/revoke` | POST | Revoke API key | Admin Key |

## Authentication

### API Key Authentication

Include your API key in the request header:

```bash
curl -H "x-api-key: your_api_key_here" \
  http://localhost:8000/company/0123456789
```

### Admin Authentication

**REST API**: Use `x-admin-key` header
**Web UI**: Login at `/admin-ui/login` with admin key

## Configuration

All configuration is managed through environment variables. See `.env.example` for required variables:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Admin
ADMIN_KEY=your_secure_admin_key

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_health.py

# Run with markers
pytest -m unit
pytest -m integration
```

### Code Quality

```bash
# Format code
black app tests

# Lint code
ruff check app tests

# Run pre-commit hooks
pre-commit run --all-files
```

### Project Structure

```
statishub/
├── app/
│   ├── api/              # API endpoints
│   │   ├── admin.py      # Admin endpoints
│   │   ├── company.py    # Company data endpoints
│   │   └── health.py     # Health check endpoints
│   ├── core/             # Core functionality
│   │   ├── auth.py       # Authentication
│   │   ├── config.py     # Configuration
│   │   ├── exceptions.py # Custom exceptions
│   │   ├── logging.py    # Logging setup
│   │   ├── middleware.py # Middleware
│   │   └── redis.py      # Redis client
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic
│   ├── adminui/          # Admin web interface
│   ├── database.py       # Database connection
│   └── main.py           # Application entry point
├── tests/                # Test suite
├── docker-compose.yml    # Docker composition
├── Dockerfile            # Docker image
├── requirements.txt      # Python dependencies
└── .env.example          # Environment template
```

## Production Deployment

### Security Checklist

- [ ] Change default admin key
- [ ] Enable HTTPS (set `COOKIE_SECURE=true`)
- [ ] Configure CORS with specific origins
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Use strong Redis password
- [ ] Regular backups of Redis data
- [ ] Monitor API usage and credits

### Monitoring

Health check endpoints for monitoring:
- `/health` - Basic application health
- `/health/redis` - Redis connection
- `/health/database` - Database connection

### Scaling

The application is stateless (except for Redis) and can be horizontally scaled:

```bash
docker-compose up -d --scale api=3
```

## Troubleshooting

### Common Issues

**Redis Connection Failed**
```bash
# Check Redis is running
redis-cli ping

# Verify REDIS_HOST and REDIS_PORT in .env
```

**Database Connection Error**
```bash
# Verify Supabase credentials
# Check SUPABASE_URL and SUPABASE_KEY in .env
```

**API Key Invalid**
```bash
# Create new API key via admin UI or REST endpoint
curl -X POST -H "x-admin-key: your_admin_key" \
  "http://localhost:8000/admin/api-keys/?client_name=Test&credits=1000"
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/statishub/issues
- Email: support@statishub.com

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.
