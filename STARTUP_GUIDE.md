# 🚀 Banking Reconciliation Engine - Complete Startup Guide

## 📋 **Quick Start Checklist**

Follow these steps in **EXACT ORDER** to start the project without issues:

### **Step 1: Start Infrastructure (Docker Services)**
```bash
# Start Kafka infrastructure
cd kafka
docker-compose up -d

# Start Backend infrastructure (PostgreSQL, Redis)
cd ../backend
docker-compose up -d

# Verify all containers are running
docker ps
```

**Expected Output:** You should see 5 containers running:
- `kafka-kafka-1` (Kafka broker - port 9092)
- `kafka-zookeeper-1` (Zookeeper - port 2181) 
- `kafka-schema_registry-1` (Schema Registry - port 8081)
- `reconciliation_postgres` (PostgreSQL - port 5433)
- `reconciliation_redis` (Redis - port 6379)

**⚠️ IMPORTANT:** Wait 15-30 seconds after starting Kafka before proceeding. Kafka takes time to initialize.

### **Step 2: Start Backend API Server**
```bash
# From project root directory
cd backend
python -m uvicorn app.main_simple:app --port 8002 --reload
```

**Expected Output:** 
```
INFO: Started server process [XXXX]
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8002
```

**Test API:** Open http://localhost:8002 - should show "Banking Reconciliation API - Working Mode"

### **Step 3: Start Frontend React App**
```bash
# Open NEW terminal, from project root
cd frontend
npm start
```

**Expected Output:**
```
Compiled successfully!
Local: http://localhost:3000
```

**Test Frontend:** Open http://localhost:3000 - should show login page

### **Step 4: Start Consumer (Transaction Processor)**
```bash
# Open NEW terminal, from project root
cd backend
python -m app.consumers.simple_reconciliation_consumer
```

**Expected Output:**
```
INFO: Started consumers for all topics: ['core_txns', 'gateway_txns', 'mobile_txns']
```

### **Step 5: Start Producer (Transaction Generator)**
```bash
# Open NEW terminal, from project root
cd producers
python coordinated_producer.py
```

**Expected Output:**
```
🚀 Starting Coordinated Transaction Producer...
✅ [CORE] Sent → Amount: ₹XXX.XX
```

---

## 🎯 **Access Points**

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend Dashboard** | http://localhost:3000 | Main application UI |
| **Backend API** | http://localhost:8002 | REST API endpoints |
| **API Documentation** | http://localhost:8002/docs | Interactive API docs |

---

## 🔐 **Login Credentials**

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Auditor** | `auditor` | `auditor123` |
| **Operator** | `operator` | `operator123` |

---

## ⚠️ **Common Issues & Solutions**

### **Issue 1: "Port already in use" Error**
```bash
# Find process using the port
netstat -ano | findstr :8002
netstat -ano | findstr :3000

# Kill the process (replace XXXX with PID)
taskkill /PID XXXX /F
```

### **Issue 2: Producer Shows "❌ Failed to send"**
**Problem:** Kafka broker not running or not ready

**Solution:**
```bash
# Check if Kafka containers are running
docker ps | findstr kafka

# If missing kafka-kafka-1, restart Kafka:
cd kafka
docker-compose down
docker-compose up -d

# Wait 15-30 seconds for Kafka to initialize
timeout /t 20

# Restart producer
cd ../producers
python coordinated_producer.py
```

### **Issue 3: Docker Containers Not Starting**
```bash
# Stop all containers
docker-compose down

# Remove old containers and restart
docker system prune -f
cd kafka && docker-compose up -d
cd ../backend && docker-compose up -d
```

### **Issue 3: Frontend Shows "Network Error"**
**Problem:** Frontend trying to connect to wrong API port

**Solution:** Check `frontend/src/App.js` - should have:
```javascript
const API_BASE = 'http://localhost:8002/api';
```

And `frontend/src/contexts/AuthContext.js` should have:
```javascript
axios.defaults.baseURL = 'http://localhost:8002';
```

### **Issue 4: Old Transactions Appearing After Restart**
**Problem:** Kafka topics contain old messages that get replayed

**Solution:** Clear Kafka topics before starting consumer:
```bash
# Set retention to 1 second to purge messages
docker exec kafka-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name core_txns --alter --add-config retention.ms=1000
docker exec kafka-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name gateway_txns --alter --add-config retention.ms=1000
docker exec kafka-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name mobile_txns --alter --add-config retention.ms=1000

# Wait 5 seconds
timeout /t 5

# Reset retention to default
docker exec kafka-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name core_txns --alter --delete-config retention.ms
docker exec kafka-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name gateway_txns --alter --delete-config retention.ms
docker exec kafka-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name mobile_txns --alter --delete-config retention.ms
```

### **Issue 5: Consumer Not Saving to Database**
**Problem:** Consumer running from wrong directory

**Solution:** Always run consumer from `backend` directory:
```bash
cd backend
python -m app.consumers.simple_reconciliation_consumer
```

**NOT from:** `cd backend/app/consumers` (this causes import issues)

---

## 🗑️ **Fresh Start (Clean Slate)**

If you want to start with zero transactions:

### **Option A: Clear Data Only (Keep Infrastructure)**
```bash
# Clear database
cd backend
python clear_all_data.py

# Clear Redis cache
docker exec reconciliation_redis redis-cli FLUSHALL

# Clear Kafka topics (see Issue 4 solution above)
```

### **Option B: Complete Reset (Nuclear Option)**
```bash
# Stop all processes (Ctrl+C in all terminals)

# Stop and remove all containers
cd kafka && docker-compose down
cd ../backend && docker-compose down

# Remove all Docker data
docker system prune -af
docker volume prune -f

# Start fresh (follow Step 1-5 above)
```

---

## 🔍 **Health Checks**

### **Verify Everything is Working:**
```bash
# 1. Check API health
curl http://localhost:8002/

# 2. Check database connection
cd backend
python -c "from app.services.database_service import db_service; print('DB OK:', db_service.get_transaction_stats())"

# 3. Check Redis
docker exec reconciliation_redis redis-cli ping

# 4. Check Kafka topics
docker exec kafka-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list
```

### **Expected Responses:**
1. API: `{"message": "Banking Reconciliation API - Working Mode", "status": "healthy"}`
2. Database: `DB OK: {'total_transactions': X, ...}`
3. Redis: `PONG`
4. Kafka: Should list `core_txns`, `gateway_txns`, `mobile_txns`

---

## 📊 **Monitoring Commands**

### **Check Transaction Flow:**
```bash
# Check producer output
# Should show: ✅ [SOURCE] Sent → Amount: ₹XXX.XX

# Check consumer output  
# Should show: ✅ txn-id: MATCHED (X sources)

# Check API data
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8002/api/transactions?limit=5
```

### **Performance Monitoring:**
```bash
# Check Docker resource usage
docker stats

# Check process status
tasklist | findstr python
tasklist | findstr node
```

---

## 🚨 **Emergency Troubleshooting**

### **If Nothing Works:**
1. **Kill all processes:** Close all terminals, restart computer
2. **Clean Docker:** `docker system prune -af && docker volume prune -f`
3. **Restart Docker Desktop**
4. **Follow startup steps 1-5 exactly**

### **If Frontend Won't Load:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### **If Database Issues:**
```bash
cd backend
python -c "
from app.db.database import engine, Base
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print('Database recreated')
"
```

---

## ✅ **Success Indicators**

**You know everything is working when:**

1. **Frontend Dashboard shows:**
   - Login page loads at http://localhost:3000
   - After login, dashboard shows live KPI cards
   - Transaction count increases over time

2. **Backend API responds:**
   - http://localhost:8002 shows API status
   - http://localhost:8002/docs shows API documentation

3. **Producer generates transactions:**
   - Terminal shows: `✅ [SOURCE] Sent → Amount: ₹XXX.XX`

4. **Consumer processes transactions:**
   - Terminal shows: `✅ txn-id: MATCHED (X sources)`

5. **Database receives data:**
   - Dashboard transaction count > 0
   - Analytics charts show data

---

## 🎯 **Pro Tips**

1. **Always start in this order:** Infrastructure → Backend → Frontend → Consumer → Producer
2. **Use separate terminals** for each service (don't run in background)
3. **Check Docker first** if anything fails (most issues are Docker-related)
4. **Clear Kafka topics** if you see old transaction data
5. **Run consumer from `backend` directory** (not `backend/app/consumers`)
6. **Wait 30-60 seconds** between starting services
7. **Use Ctrl+F5** to refresh browser if dashboard doesn't update

---

## 📞 **Quick Commands Reference**

```bash
# Start everything (run each in separate terminal)
cd kafka && docker-compose up -d
cd backend && docker-compose up -d
cd backend && python -m uvicorn app.main_simple:app --port 8002 --reload
cd frontend && npm start
cd backend && python -m app.consumers.simple_reconciliation_consumer
cd producers && python coordinated_producer.py

# Stop everything
# Ctrl+C in all terminals, then:
cd kafka && docker-compose down
cd backend && docker-compose down

# Clean restart
cd backend && python clear_all_data.py
docker exec reconciliation_redis redis-cli FLUSHALL
# + Clear Kafka topics (see Issue 4)
```

---

**🎉 Your Banking Reconciliation Engine with Enhanced Analytics is Ready!**

*This guide covers all the issues we encountered today and provides solutions for future startups.*