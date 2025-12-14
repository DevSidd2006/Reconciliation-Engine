# 🚀 Banking Reconciliation Engine - Quick Reference

## 📋 **System Commands**

### **Infrastructure**
```bash
# Start all infrastructure
cd kafka && docker-compose up -d
cd ../backend && docker-compose up -d

# Check running services
docker ps

# View logs
docker logs reconciliation_postgres
docker logs reconciliation_redis
docker logs kafka-kafka-1
```

### **Backend Services**
```bash
# Start API server
cd backend/app
uvicorn main:app --reload --port 8000

# Start consumer
cd backend/app/consumers
python simple_reconciliation_consumer.py

# Start producers
cd producers
python coordinated_producer.py

# Run tests
cd backend
python test_redis_performance.py
python test_security_features.py
```

### **Frontend**
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm start

# Build for production
npm run build
```

## 🔗 **Access Points**

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend Dashboard** | http://localhost:3001 | Main application UI |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Health Check** | http://localhost:8000/api/health | System status |
| **Redis Stats** | http://localhost:8000/api/redis-stats | Cache performance |

## 📊 **Key Endpoints**

### **Public Endpoints**
- `GET /api/health` - System health status
- `GET /docs` - API documentation
- `GET /redoc` - Alternative API docs

### **Secured Endpoints** (Require Authentication)
- `GET /api/transactions` - Transaction listing
- `GET /api/mismatches` - Mismatch reports
- `GET /api/stats` - System statistics
- `GET /api/redis-stats` - Cache performance
- `GET /api/reconciliation-details` - Reconciliation data

## 🔐 **Demo Users**

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| 👑 **Admin** | `admin` | `admin123` | Full system access (12 permissions) |
| 🔍 **Auditor** | `auditor` | `auditor123` | Read-only access (6 permissions) |
| ⚙️ **Operator** | `operator` | `operator123` | Limited operations (3 permissions) |

## 📈 **Performance Metrics**

### **Current System Performance**
```
🔥 LIVE METRICS
├── Transactions: 1,200+ processed
├── Mismatches: 800+ detected
├── Redis Hit Ratio: 87.41%
├── API Response: <50ms
├── Cache Ops: 3,000+/sec
└── Database: <25ms queries
```

### **Expected Benchmarks**
- **Transaction Processing**: 100+ per minute
- **API Response Time**: <100ms (target <50ms)
- **Redis Cache Hit Ratio**: >80% (achieved 87%+)
- **Database Query Time**: <50ms (achieved <25ms)
- **System Availability**: >99% uptime

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **Port Already in Use**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

#### **Docker Issues**
```bash
# Restart services
docker-compose down && docker-compose up -d

# Clean system
docker system prune -f
```

#### **Database Connection**
```bash
# Reset database
cd backend/app
python recreate_tables.py

# Check connection
python test_db_connection.py
```

#### **Redis Connection**
```bash
# Test Redis
curl http://localhost:8000/api/redis-stats

# Check Redis container
docker logs reconciliation_redis
```

### **Health Checks**
```bash
# System health
curl http://localhost:8000/api/health

# Redis performance
curl http://localhost:8000/api/redis-stats

# Database status
curl http://localhost:8000/api/stats
```

## 🔧 **Configuration**

### **Environment Variables**
```env
# Backend (.env)
POSTGRES_PASSWORD=postgres123
DATABASE_URL=postgresql://postgres:postgres123@localhost:5433/reconciliation_db
REDIS_URL=redis://localhost:6379/0
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Frontend (.env)
REACT_APP_API_BASE_URL=http://localhost:8000
```

### **Default Ports**
- **Frontend**: 3001
- **Backend API**: 8000
- **PostgreSQL**: 5433
- **Redis**: 6379
- **Kafka**: 9092
- **Zookeeper**: 2181
- **Keycloak**: 8080 (optional)

## 📊 **Monitoring Commands**

### **System Status**
```bash
# Check all services
docker ps

# View system resources
docker stats

# Check logs
docker-compose logs -f
```

### **Performance Testing**
```bash
# Redis performance test
cd backend
python test_redis_performance.py

# Security test suite
python test_security_features.py

# API load test (manual)
for i in {1..100}; do curl http://localhost:8000/api/health; done
```

### **Database Queries**
```sql
-- Transaction counts by source
SELECT source, COUNT(*) FROM transactions GROUP BY source;

-- Reconciliation status
SELECT reconciliation_status, COUNT(*) FROM transactions GROUP BY reconciliation_status;

-- Recent mismatches
SELECT * FROM mismatches ORDER BY detected_at DESC LIMIT 10;
```

## 🚀 **Development Workflow**

### **Starting Development**
1. Start infrastructure: `docker-compose up -d`
2. Initialize database: `python recreate_tables.py`
3. Start backend: `uvicorn main:app --reload --port 8000`
4. Start consumer: `python simple_reconciliation_consumer.py`
5. Start producer: `python coordinated_producer.py`
6. Start frontend: `npm start`

### **Testing Changes**
1. Run health check: `curl http://localhost:8000/api/health`
2. Test Redis: `python test_redis_performance.py`
3. Test security: `python test_security_features.py`
4. Check frontend: Open http://localhost:3001

### **Production Deployment**
1. Build frontend: `npm run build`
2. Configure environment variables
3. Set up SSL certificates
4. Configure reverse proxy (Nginx)
5. Set up monitoring and logging
6. Configure backup procedures

## 📚 **Additional Resources**

- **[Complete Installation Guide](INSTALLATION_GUIDE.md)**
- **[Security Implementation](SECURITY_IMPLEMENTATION.md)**
- **[API Documentation](http://localhost:8000/docs)** (when running)
- **[Project README](README.md)**

## 🎯 **Quick Status Check**

Run this command to verify everything is working:

```bash
# One-liner system check
curl -s http://localhost:8000/api/health | grep -q "IDLE\|HEALTHY" && echo "✅ System OK" || echo "❌ System Issue"
```

**Your Banking Reconciliation Engine Quick Reference** 🏦⚡