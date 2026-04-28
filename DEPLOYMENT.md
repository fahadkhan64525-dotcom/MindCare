# MindCare Backend - Production Deployment Guide

How to deploy MindCare API to production environments.

---

## Pre-Deployment Checklist

- [ ] All tests passing (`python test_api.py`)
- [ ] Model trained and validated
- [ ] Environment variables configured
- [ ] Logs directory created
- [ ] Database backup procedure established
- [ ] Security review completed
- [ ] SSL/TLS certificates prepared (if applicable)

---

## Option 1: Heroku Deployment

### Step 1: Create Heroku App
```bash
heroku create your-mindcare-app
```

### Step 2: Add Procfile
Create `Procfile`:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
package: python train_model.py
```

### Step 3: Set Environment Variables
```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set DB_PATH=/tmp/mental_health.db
```

### Step 4: Deploy
```bash
git push heroku main
```

### Step 5: Run Model Training
```bash
heroku run python train_model.py
```

---

## Option 2: Docker Deployment

### Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create log directory
RUN mkdir -p /app/logs

# Train model
RUN python train_model.py

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Create docker-compose.yml
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key
    volumes:
      - ./mental_health.db:/app/mental_health.db
      - ./app.log:/app/app.log
```

### Deploy
```bash
docker-compose up -d
```

---

## Option 3: AWS Elastic Beanstalk

### Step 1: Create Application
```bash
eb init -p python-3.9 mindcare-api
```

### Step 2: Create Environment
```bash
eb create production
```

### Step 3: Configure Environment
Create `.ebextensions/python.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    FLASK_ENV: production
    PYTHONPATH: /var/app/current:$PYTHONPATH
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
```

### Step 4: Deploy
```bash
eb deploy
```

---

## Option 4: Traditional VPS (DigitalOcean, Linode, etc.)

### Step 1: SSH into Server
```bash
ssh root@your-server-ip
```

### Step 2: Install Dependencies
```bash
apt update && apt upgrade -y
apt install python3-pip python3-venv nginx supervisor -y

# Install PM2 (optional, for process management)
npm install -g pm2
```

### Step 3: Create Application Directory
```bash
mkdir -p /var/www/mindcare-api
cd /var/www/mindcare-api
```

### Step 4: Clone Repository and Setup
```bash
# Clone your repo (or upload files)
git clone your-repo-url .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Train model
python train_model.py

# Create log directory
mkdir -p logs
```

### Step 5: Configure Gunicorn with Supervisor
Create `/etc/supervisor/conf.d/mindcare.conf`:
```ini
[program:mindcare]
command=/var/www/mindcare-api/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
directory=/var/www/mindcare-api
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/mindcare-api/logs/gunicorn.log
environment=PATH="/var/www/mindcare-api/venv/bin",FLASK_ENV="production"
```

### Step 6: Start Service
```bash
supervisorctl reread
supervisorctl update
supervisorctl start mindcare
```

### Step 7: Configure Nginx
Create `/etc/nginx/sites-available/mindcare`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/mindcare-api/static;
    }
}
```

### Step 8: Enable Site
```bash
ln -s /etc/nginx/sites-available/mindcare /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 9: Setup SSL (Let's Encrypt)
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

---

## Database Considerations

### For Production
1. **Use PostgreSQL instead of SQLite**
   ```bash
   pip install psycopg2-binary
   ```

   Modify `app.py` database functions:
   ```python
   import psycopg2
   
   DB_CONFIG = {
       'host': os.getenv('DB_HOST'),
       'database': os.getenv('DB_NAME'),
       'user': os.getenv('DB_USER'),
       'password': os.getenv('DB_PASSWORD')
   }
   
   conn = psycopg2.connect(**DB_CONFIG)
   ```

2. **Backup Strategy**
   ```bash
   # Daily backup
   0 2 * * * pg_dump mindcare_db > /backups/mindcare_$(date +\%Y\%m\%d).sql
   ```

3. **Enable Connection Pooling**
   ```bash
   pip install pgbouncer
   ```

---

## Security Best Practices

### 1. Environment Variables
```bash
# Production .env
FLASK_ENV=production
SECRET_KEY=generate-with-secrets-library
CORS_ORIGINS=https://your-frontend-domain.com
DB_HOST=secure-db-host
LOG_LEVEL=WARNING
```

### 2. HTTPS/SSL
- Always use HTTPS in production
- Use Let's Encrypt for free certificates
- Set `SECURE_SSL_REDIRECT=True`

### 3. Rate Limiting
```bash
pip install Flask-Limiter

from flask_limiter import Limiter
limiter = Limiter(app)

@app.route('/predict', methods=['POST'])
@limiter.limit("100 per hour")
def predict_stress():
    ...
```

### 4. CORS Configuration
```python
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('CORS_ORIGINS', '*').split(','),
        "methods": ["GET", "POST", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})
```

### 5. Input Validation (Already Implemented)
- All inputs validated
- Message sanitization
- Length limits

### 6. Logging
- Set `LOG_LEVEL=WARNING` or `ERROR` in production
- Store logs securely
- Implement log rotation

---

## Monitoring & Maintenance

### Application Monitoring
```bash
# Check application status
curl https://your-domain.com/health

# View logs
tail -f /var/www/mindcare-api/logs/app.log

# Check process
supervisorctl status mindcare
```

### Database Monitoring
```bash
# Check database
psql -h db-host -U user -d mindcare_db -c "SELECT COUNT(*) FROM mood_entries;"

# Backup
pg_dump mindcare_db > backup.sql
```

### Resource Monitoring
```bash
# CPU and Memory
top

# Disk space
df -h

# Network
netstat -tulpn | grep gunicorn
```

---

## Performance Optimization

### 1. Model Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def predict_stress_cached(mood, sleep, screen_time, workload):
    # Predictions are cached
    pass
```

### 2. Database Indexing
```sql
CREATE INDEX idx_date_mood ON mood_entries(date, mood);
CREATE INDEX idx_date ON mood_entries(date);
```

### 3. Redis Caching
```bash
pip install redis flask-caching

from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/analytics', methods=['GET'])
@cache.cached(timeout=300)
def get_analytics():
    ...
```

### 4. Load Balancing
Use Nginx/HAProxy to distribute traffic:
```nginx
upstream mindcare {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}
```

---

## Scaling Strategy

### Vertical Scaling
- Increase server resources
- Upgrade database
- Add more workers

### Horizontal Scaling
```bash
# Run multiple instances
gunicorn -w 8 -b 0.0.0.0:5000 app:app       # Instance 1
gunicorn -w 8 -b 0.0.0.0:5001 app:app       # Instance 2
gunicorn -w 8 -b 0.0.0.0:5002 app:app       # Instance 3
gunicorn -w 8 -b 0.0.0.0:5003 app:app       # Instance 4

# Load balance with Nginx
```

### Database Scaling
- Read replicas
- Connection pooling
- Sharding for large datasets

---

## Troubleshooting

### Problem: 502 Bad Gateway
```bash
# Check logs
tail -f /var/www/mindcare-api/logs/gunicorn.log

# Restart service
supervisorctl restart mindcare
```

### Problem: Slow Response
```bash
# Check database
psql -c "ANALYZE mindcare_db;"

# Monitor resources
top

# Check caching
redis-cli ping
```

### Problem: Database Connection Error
```bash
# Test connection
psql -h db-host -U user -d mindcare_db -c "SELECT 1;"

# Check pool
pgbouncer -R
```

---

## Rollback Procedure

```bash
# Backup current version
mv /var/www/mindcare-api /var/www/mindcare-api.backup

# Restore previous version
cp -r /backups/mindcare-api.v1 /var/www/mindcare-api

# Restart service
supervisorctl restart mindcare
```

---

## Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Database backup | Daily | `pg_dump mindcare_db > backup.sql` |
| Log rotation | Weekly | `logrotate /etc/logrotate.d/mindcare` |
| Model retraining | Monthly | `python train_model.py` |
| Security updates | As needed | `apt update && apt upgrade` |
| Performance optimization | Quarterly | Review metrics and tune |

---

## Useful Commands

```bash
# Production startup
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With SSL
gunicorn --certfile=/etc/letsencrypt/live/domain/fullchain.pem \
         --keyfile=/etc/letsencrypt/live/domain/privkey.pem \
         -w 4 -b 0.0.0.0:443 app:app

# Check deployment
curl https://your-domain.com/health

# View logs
tail -100f app.log

# Monitor
watch -n 1 'curl -s https://your-domain.com/health | jq'
```

---

## Support & Documentation

- **Full Backend Docs**: See README.md
- **Quick Start**: See QUICKSTART.md
- **Improvements**: See IMPROVEMENTS.md
- **Testing**: Run `python test_api.py`

---

**Production Ready! 🚀**

---

**Last Updated**: February 6, 2026
**Version**: 1.0.0
