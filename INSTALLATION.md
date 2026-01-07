# Installation Guide

Complete installation instructions for Statishub Company API.

## Table of Contents

- [System Requirements](#system-requirements)
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Configuration](#configuration)
- [Verification](#verification)

## System Requirements

### Minimum Requirements

- **OS**: Linux, macOS, or Windows with WSL2
- **Python**: 3.11 or higher
- **Redis**: 7.0 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 1GB free space

### External Services

- **Supabase** account (or PostgreSQL 14+)
- **Docker** (optional, for containerized deployment)

## Development Setup

### 1. Install Python

**macOS (using Homebrew)**
```bash
brew install python@3.11
```

**Ubuntu/Debian**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Windows**
Download from [python.org](https://www.python.org/downloads/)

### 2. Install Redis

**macOS**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Docker**
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

### 3. Clone Repository

```bash
git clone https://github.com/yourusername/statishub.git
cd statishub
```

### 4. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_or_service_key
ADMIN_KEY=generate_secure_random_key

# Optional (defaults shown)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### 7. Verify Installation

```bash
# Check Python version
python --version

# Check Redis connection
redis-cli ping

# Run tests
pytest

# Start application
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs to verify API is running.

## Production Deployment

### Option 1: Docker Compose (Recommended)

**1. Install Docker & Docker Compose**

Follow official guides:
- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

**2. Configure Environment**

```bash
cp .env.example .env
# Edit .env with production values
```

**3. Start Services**

```bash
docker-compose up -d
```

**4. Verify Deployment**

```bash
# Check containers
docker-compose ps

# View logs
docker-compose logs -f api

# Health check
curl http://localhost:8000/health
```

### Option 2: Systemd Service (Linux)

**1. Install Dependencies**

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv redis-server nginx
```

**2. Setup Application**

```bash
sudo useradd -m -s /bin/bash statishub
sudo su - statishub
git clone https://github.com/yourusername/statishub.git
cd statishub
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env
exit
```

**3. Create Systemd Service**

Create `/etc/systemd/system/statishub.service`:

```ini
[Unit]
Description=Statishub Company API
After=network.target redis.service

[Service]
Type=notify
User=statishub
Group=statishub
WorkingDirectory=/home/statishub/statishub
Environment="PATH=/home/statishub/statishub/venv/bin"
ExecStart=/home/statishub/statishub/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**4. Start Service**

```bash
sudo systemctl daemon-reload
sudo systemctl start statishub
sudo systemctl enable statishub
sudo systemctl status statishub
```

**5. Configure Nginx Reverse Proxy**

Create `/etc/nginx/sites-available/statishub`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/statishub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**6. Setup SSL (Optional but Recommended)**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | Yes | - | Supabase project URL |
| `SUPABASE_KEY` | Yes | - | Supabase anon/service key |
| `ADMIN_KEY` | Yes | - | Admin authentication key |
| `REDIS_HOST` | No | localhost | Redis server host |
| `REDIS_PORT` | No | 6379 | Redis server port |
| `REDIS_DB` | No | 0 | Redis database number |
| `ENVIRONMENT` | No | production | Environment name |
| `DEBUG` | No | false | Enable debug mode |
| `LOG_LEVEL` | No | INFO | Logging level |
| `ALLOWED_ORIGINS` | No | * | CORS allowed origins |
| `COOKIE_SECURE` | No | true | Secure cookie flag |

### Generating Secure Keys

```bash
# Generate admin key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use OpenSSL
openssl rand -base64 32
```

## Verification

### Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Redis health
curl http://localhost:8000/health/redis

# Database health
curl http://localhost:8000/health/database
```

### Create First API Key

```bash
# Via API
curl -X POST "http://localhost:8000/admin/api-keys/?client_name=TestClient&credits=1000" \
  -H "x-admin-key: your_admin_key"

# Via Admin UI
# Visit http://localhost:8000/admin-ui/login
```

### Test API Request

```bash
curl -H "x-api-key: your_api_key" \
  http://localhost:8000/company/0123456789
```

## Troubleshooting

### Application Won't Start

```bash
# Check Python version
python --version

# Check dependencies
pip install -r requirements.txt

# Check .env file
cat .env

# Run with verbose logging
LOG_LEVEL=DEBUG uvicorn app.main:app
```

### Redis Connection Error

```bash
# Check Redis is running
redis-cli ping

# Check Redis port
netstat -an | grep 6379

# Test connection
redis-cli -h localhost -p 6379 ping
```

### Permission Errors (Docker)

```bash
# Fix volume permissions
sudo chown -R 1000:1000 redis-data/

# Rebuild containers
docker-compose down -v
docker-compose up --build -d
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000
# Or
netstat -an | grep 8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8080
```

## Next Steps

- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production best practices
- See [README.md](README.md) for API usage
- Check [CLAUDE.md](CLAUDE.md) for architecture details
- Review security checklist in production deployment section
