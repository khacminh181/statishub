# Deployment Guide

Production deployment guide for Statishub Company API.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Deployment Options](#deployment-options)
- [Security Configuration](#security-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Scaling](#scaling)

## Pre-Deployment Checklist

### Security

- [ ] Change default `ADMIN_KEY` to strong random value
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Configure `ALLOWED_ORIGINS` with specific domains (not `*`)
- [ ] Enable `COOKIE_SECURE=true` for HTTPS
- [ ] Use HTTPS/TLS certificates
- [ ] Configure Redis password if exposed
- [ ] Review and restrict network access

### Configuration

- [ ] Verify all environment variables are set
- [ ] Test Supabase connection
- [ ] Test Redis connection
- [ ] Configure proper log levels
- [ ] Set up error monitoring (optional)
- [ ] Configure rate limiting appropriately

### Testing

- [ ] All tests passing (`pytest`)
- [ ] Load testing completed
- [ ] Security scanning done
- [ ] Manual API testing performed
- [ ] Health checks responding correctly

### Infrastructure

- [ ] Redis persistence configured
- [ ] Backups scheduled
- [ ] Monitoring alerts set up
- [ ] SSL certificates installed
- [ ] Reverse proxy configured
- [ ] Firewall rules applied

## Deployment Options

### 1. Docker Compose (Single Server)

**Best for**: Small to medium deployments, single server

**Pros**: Easy setup, bundled services, quick deployment
**Cons**: Single point of failure, limited scaling

```bash
# 1. Clone repository
git clone https://github.com/yourusername/statishub.git
cd statishub

# 2. Configure production environment
cp .env.example .env
nano .env  # Edit with production values

# 3. Deploy
docker-compose up -d

# 4. Verify
docker-compose ps
curl http://localhost:8000/health
```

**Production Enhancements**:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - /data/redis:/data
```

### 2. Cloud Platform (AWS/GCP/Azure)

**Best for**: Production deployments requiring high availability

#### AWS Deployment (ECS Fargate)

1. **Build and push image**:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t statishub-api .
docker tag statishub-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/statishub-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/statishub-api:latest
```

2. **Create ECS task definition** with environment variables
3. **Setup Application Load Balancer**
4. **Configure Auto Scaling**
5. **Use ElastiCache for Redis**

#### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/statishub-api
gcloud run deploy statishub-api \
  --image gcr.io/PROJECT-ID/statishub-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "SUPABASE_URL=...,SUPABASE_KEY=..."
```

### 3. Kubernetes

**Best for**: Large scale, multi-region deployments

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: statishub-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: statishub-api
  template:
    metadata:
      labels:
        app: statishub-api
    spec:
      containers:
      - name: api
        image: statishub-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: SUPABASE_URL
          valueFrom:
            secretKeyRef:
              name: statishub-secrets
              key: supabase-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

## Security Configuration

### HTTPS/TLS Setup

**Using Nginx with Let's Encrypt**:

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Firewall Rules

```bash
# Allow HTTP, HTTPS, SSH only
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Block Redis from external access
sudo ufw deny 6379/tcp
```

### Redis Security

```bash
# Add to redis.conf
requirepass your_strong_redis_password
bind 127.0.0.1
protected-mode yes
```

Update `.env`:
```bash
REDIS_HOST=localhost
REDIS_PASSWORD=your_strong_redis_password
```

## Monitoring & Logging

### Health Check Monitoring

**Using cron + curl**:

```bash
# /etc/cron.d/statishub-monitor
*/5 * * * * curl -f http://localhost:8000/health || echo "Health check failed" | mail -s "Statishub Alert" admin@yourdomain.com
```

**Using external monitoring**:
- [UptimeRobot](https://uptimerobot.com/)
- [Pingdom](https://www.pingdom.com/)
- AWS CloudWatch
- Google Cloud Monitoring

### Centralized Logging

**Using Docker logging driver**:

```yaml
# docker-compose.yml
services:
  api:
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://logs.yourdomain.com:514"
        tag: "statishub-api"
```

**Log aggregation tools**:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Grafana Loki
- AWS CloudWatch Logs
- Google Cloud Logging

### Application Metrics

Monitor these key metrics:
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (5xx responses)
- API key credit consumption
- Cache hit/miss ratio
- Redis memory usage
- Database query time

## Backup & Recovery

### Redis Data Backup

**Automated backups**:

```bash
# /etc/cron.daily/redis-backup
#!/bin/bash
BACKUP_DIR=/backups/redis
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
redis-cli BGSAVE
sleep 5
cp /var/lib/redis/dump.rdb ${BACKUP_DIR}/dump_${DATE}.rdb

# Keep only last 7 days
find ${BACKUP_DIR} -name "dump_*.rdb" -mtime +7 -delete

# Upload to S3 (optional)
aws s3 cp ${BACKUP_DIR}/dump_${DATE}.rdb s3://your-bucket/redis-backups/
```

Make executable:
```bash
chmod +x /etc/cron.daily/redis-backup
```

### Restore from Backup

```bash
# Stop Redis
sudo systemctl stop redis

# Restore backup
sudo cp /backups/redis/dump_20240101_120000.rdb /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb

# Start Redis
sudo systemctl start redis
```

### Disaster Recovery Plan

1. **Database (Supabase)**: Automatic backups provided by Supabase
2. **Redis**: Daily backups with 7-day retention
3. **Application Code**: Version controlled in Git
4. **Configuration**: Secure backup of `.env` file

**Recovery Time Objective (RTO)**: 1 hour
**Recovery Point Objective (RPO)**: 24 hours

## Scaling

### Horizontal Scaling

**Using Docker Compose**:
```bash
docker-compose up -d --scale api=3
```

**Using Load Balancer** (Nginx):

```nginx
upstream api_backend {
    least_conn;
    server 10.0.1.10:8000;
    server 10.0.1.11:8000;
    server 10.0.1.12:8000;
}

server {
    location / {
        proxy_pass http://api_backend;
    }
}
```

### Vertical Scaling

Increase container resources:

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

### Redis Scaling

For high traffic, consider:
- Redis Cluster for sharding
- Redis Sentinel for high availability
- Redis Enterprise
- AWS ElastiCache with Multi-AZ

### Database Connection Pooling

Already configured in Supabase client, but monitor:
- Connection pool size
- Connection timeout
- Query performance

## Performance Optimization

### Caching Strategy

Current cache TTL: 3600 seconds (1 hour)

Adjust based on data freshness requirements:

```python
# app/api/company.py
redis_client.setex(cache_key, 7200, json.dumps(res.data))  # 2 hours
```

### CDN Integration

For static assets and API responses:
- CloudFlare
- AWS CloudFront
- Fastly

### Database Optimization

- Ensure proper indexes on Supabase tables
- Monitor slow queries
- Use connection pooling
- Consider read replicas for heavy read workloads

## Rollback Procedure

### Docker Deployment

```bash
# Tag current version before deploying
docker tag statishub-api:latest statishub-api:backup

# Deploy new version
docker-compose pull
docker-compose up -d

# If issues, rollback
docker tag statishub-api:backup statishub-api:latest
docker-compose up -d
```

### Systemd Service

```bash
# Keep previous version
cd /home/statishub
mv statishub statishub-backup
git clone https://github.com/yourusername/statishub.git

# If issues, rollback
sudo systemctl stop statishub
rm -rf statishub
mv statishub-backup statishub
sudo systemctl start statishub
```

## Maintenance Windows

Recommended maintenance schedule:
- **Minor updates**: Any time (zero downtime with load balancer)
- **Major updates**: Off-peak hours (2-4 AM local time)
- **Database migrations**: Coordinate with Supabase maintenance windows

## Support Contacts

- **Application Issues**: DevOps team
- **Database Issues**: Supabase support
- **Infrastructure Issues**: Cloud provider support
