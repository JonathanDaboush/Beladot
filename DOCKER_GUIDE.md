# Beladot E-Commerce Platform - Docker Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker Desktop installed and running
- Docker Compose v2.0+

### 1. Environment Configuration

#### Backend Configuration
Copy the example environment file and configure:
```bash
cp Ecommerce/backend/.env.example Ecommerce/backend/.env
```

Edit `Ecommerce/backend/.env` with your credentials:
- Update `SECRET_KEY` with a secure random string (32+ characters)
- Configure SMTP settings for email functionality
- Adjust `ALLOWED_ORIGINS` for production

#### Frontend Configuration  
Copy the example environment file:
```bash
cp front-end/.env.example front-end/.env
```

For production, update `REACT_APP_API_URL` to your backend domain.

### 2. Start All Services

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL Database** on port 5432
- **Backend API** on port 8000  
- **Frontend App** on port 3000

### 3. Verify Services

Check all services are running:
```bash
docker-compose ps
```

View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (username: `beladot_user`, password: `beladot_password_2024`)

### 5. Initial Setup

#### Create Admin User (if needed)
```bash
docker-compose exec backend python -c "from setup_test_db import create_admin; create_admin()"
```

#### Run Database Migrations
Migrations run automatically on startup, but you can trigger manually:
```bash
docker-compose exec backend alembic upgrade head
```

## Development Workflow

### Hot Reload
Both backend and frontend support hot reload in development mode:
- Backend: Code changes auto-reload with `--reload` flag
- Frontend: React hot module replacement enabled

### Run Tests
```bash
# Backend tests
docker-compose exec backend pytest

# Specific test file
docker-compose exec backend pytest Tests/test_new_features.py -v

# With coverage
docker-compose exec backend pytest --cov=. --cov-report=html
```

### Database Access
Connect to PostgreSQL:
```bash
docker-compose exec postgres psql -U beladot_user -d beladot_db
```

### Reset Database
```bash
docker-compose down -v
docker-compose up -d
```

## Production Deployment

### 1. Update Environment Variables
- Set `ENVIRONMENT=production` in backend .env
- Use strong `SECRET_KEY` (generate with `openssl rand -hex 32`)
- Configure production database URL
- Set up production SMTP credentials
- Update `ALLOWED_ORIGINS` with your frontend domain

### 2. Build Production Images
```bash
docker-compose -f docker-compose.prod.yml build
```

### 3. SSL/TLS Setup
Use nginx or Caddy as reverse proxy for SSL:

```yaml
# docker-compose.prod.yml addition
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/nginx/ssl
  depends_on:
    - backend
    - frontend
```

### 4. Scale Services
```bash
# Scale backend instances
docker-compose up -d --scale backend=3
```

## Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Database connection failed → Check DATABASE_URL in .env
# - Port already in use → Stop conflicting service or change port mapping
```

### Frontend Build Errors
```bash
# Rebuild without cache
docker-compose build --no-cache frontend

# Check Node.js logs
docker-compose logs frontend
```

### Database Connection Issues
```bash
# Verify PostgreSQL is healthy
docker-compose exec postgres pg_isready

# Check connection from backend
docker-compose exec backend python -c "from database import engine; print(engine.connect())"
```

### Clear All Data (Fresh Start)
```bash
# Stop and remove everything including volumes
docker-compose down -v

# Remove orphan containers
docker-compose down --remove-orphans

# Start fresh
docker-compose up -d
```

## Service Management

### Stop Services
```bash
docker-compose stop
```

### Restart Services
```bash
docker-compose restart
```

### Update Images
```bash
# Pull latest base images
docker-compose pull

# Rebuild with new code
docker-compose build

# Restart with new images
docker-compose up -d
```

### View Resource Usage
```bash
docker stats
```

## Backup and Restore

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U beladot_user beladot_db > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T postgres psql -U beladot_user -d beladot_db < backup_20240101.sql
```

### Uploads Backup
```bash
# Backup uploads volume
docker run --rm -v beladot_uploads_data:/data -v $(pwd):/backup alpine tar czf /backup/uploads_backup.tar.gz -C /data .

# Restore uploads
docker run --rm -v beladot_uploads_data:/data -v $(pwd):/backup alpine tar xzf /backup/uploads_backup.tar.gz -C /data
```

## Performance Tuning

### PostgreSQL Optimization
Add to `docker-compose.yml` under postgres service:
```yaml
command:
  - "postgres"
  - "-c"
  - "max_connections=200"
  - "-c"
  - "shared_buffers=256MB"
  - "-c"
  - "effective_cache_size=1GB"
```

### Backend Optimization
- Use Gunicorn with multiple workers for production
- Enable Redis for caching
- Configure connection pooling

## Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready
```

### Log Aggregation
```bash
# Export logs
docker-compose logs > logs_$(date +%Y%m%d).txt

# Follow specific service logs
docker-compose logs -f backend --tail=100
```

## Security Checklist

- [ ] Change default database credentials
- [ ] Generate secure `SECRET_KEY`
- [ ] Enable HTTPS in production
- [ ] Set restrictive CORS origins
- [ ] Use app-specific passwords for SMTP
- [ ] Enable firewall rules
- [ ] Regular security updates (`docker-compose pull`)
- [ ] Backup encryption
- [ ] Environment variables not committed to git

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Deployment](https://create-react-app.dev/docs/deployment/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
