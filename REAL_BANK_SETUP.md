# Real Bank Integration Setup Guide

## Quick Start: Connecting to Real Banks

### Phase 1: Preparation (Week 1)

#### 1.1 Identify Your Banks
- [ ] List all banks you want to integrate with
- [ ] Identify transaction sources (APIs, SFTP, files)
- [ ] Document transaction volumes

**Example Banks:**
- HDFC Bank
- ICICI Bank
- SBI (State Bank of India)
- Axis Bank
- Kotak Bank
- Razorpay (Payment Gateway)

#### 1.2 Contact Bank Support
Send emails to each bank's developer support:

**HDFC Bank**
- Email: api-support@hdfcbank.com
- Portal: https://developer.hdfcbank.com
- Request: API access for transaction feeds

**ICICI Bank**
- Email: developer@icicibank.com
- Portal: https://developer.icicibank.com
- Request: API credentials and documentation

**SBI**
- Email: api-support@sbi.co.in
- Portal: https://developer.sbi.co.in
- Request: OAuth 2.0 credentials

**Razorpay**
- Dashboard: https://dashboard.razorpay.com
- Settings → API Keys
- Copy Key ID and Key Secret

---

### Phase 2: Configuration (Week 2)

#### 2.1 Create Environment File

Create `.env` file in project root:

```bash
# HDFC Bank
HDFC_API_TOKEN=your_hdfc_api_token_here
HDFC_API_URL=https://api.hdfcbank.com

# ICICI Bank
ICICI_API_TOKEN=your_icici_api_token_here
ICICI_API_KEY=your_icici_api_key_here
ICICI_API_URL=https://api.icicibank.com

# SBI
SBI_CLIENT_ID=your_sbi_client_id_here
SBI_CLIENT_SECRET=your_sbi_client_secret_here
SBI_API_URL=https://api.sbi.co.in

# Razorpay
RAZORPAY_KEY=your_razorpay_key_here
RAZORPAY_SECRET=your_razorpay_secret_here

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/reconciliation_db
```

#### 2.2 Install Required Libraries

```bash
pip install requests paramiko cryptography python-dotenv
```

#### 2.3 Update Requirements

Add to `producers/requirements.txt`:

```
requests==2.31.0
paramiko==3.4.0
cryptography==41.0.7
python-dotenv==1.0.0
kafka-python==2.0.2
```

---

### Phase 3: Testing (Week 3)

#### 3.1 Test Individual Bank Connections

```python
# test_bank_connections.py

from producers.bank_adapter import BankDataAdapter
import os

adapter = BankDataAdapter()

print("Testing Bank Connections...")
print("=" * 50)

# Test HDFC
print("\n1. Testing HDFC Bank...")
try:
    count = adapter.fetch_from_hdfc_api()
    print(f"✅ HDFC: Successfully fetched {count} transactions")
except Exception as e:
    print(f"❌ HDFC: {e}")

# Test ICICI
print("\n2. Testing ICICI Bank...")
try:
    count = adapter.fetch_from_icici_api()
    print(f"✅ ICICI: Successfully fetched {count} transactions")
except Exception as e:
    print(f"❌ ICICI: {e}")

# Test SBI
print("\n3. Testing SBI...")
try:
    count = adapter.fetch_from_sbi_api()
    print(f"✅ SBI: Successfully fetched {count} transactions")
except Exception as e:
    print(f"❌ SBI: {e}")

# Test Razorpay
print("\n4. Testing Razorpay...")
try:
    count = adapter.fetch_from_razorpay()
    print(f"✅ Razorpay: Successfully fetched {count} transactions")
except Exception as e:
    print(f"❌ Razorpay: {e}")

print("\n" + "=" * 50)
print("Connection tests complete!")
```

Run tests:
```bash
python test_bank_connections.py
```

#### 3.2 Verify Kafka Topics

```bash
# Create topics for each bank
docker exec kafka-kafka-1 kafka-topics --create --topic hdfc_txns --bootstrap-server localhost:9092
docker exec kafka-kafka-1 kafka-topics --create --topic icici_txns --bootstrap-server localhost:9092
docker exec kafka-kafka-1 kafka-topics --create --topic sbi_txns --bootstrap-server localhost:9092
docker exec kafka-kafka-1 kafka-topics --create --topic razorpay_txns --bootstrap-server localhost:9092

# List topics
docker exec kafka-kafka-1 kafka-topics --list --bootstrap-server localhost:9092
```

#### 3.3 Test Data Flow

```bash
# Terminal 1: Start producer
python producers/bank_adapter.py

# Terminal 2: Monitor Kafka
docker exec kafka-kafka-1 kafka-console-consumer --topic hdfc_txns --bootstrap-server localhost:9092 --from-beginning

# Terminal 3: Check database
psql -U postgres -d reconciliation_db -c "SELECT COUNT(*) FROM transactions;"
```

---

### Phase 4: Deployment (Week 4)

#### 4.1 Create Production Producer

Create `producers/production_bank_producer.py`:

```python
import time
import schedule
import logging
from bank_adapter import BankDataAdapter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bank_producer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionBankProducer:
    def __init__(self):
        self.adapter = BankDataAdapter()
        self.total_transactions = 0
    
    def fetch_all_banks(self):
        """Fetch from all banks"""
        logger.info("Starting bank transaction fetch...")
        
        banks = [
            ('HDFC', self.adapter.fetch_from_hdfc_api),
            ('ICICI', self.adapter.fetch_from_icici_api),
            ('SBI', self.adapter.fetch_from_sbi_api),
            ('Razorpay', self.adapter.fetch_from_razorpay),
        ]
        
        for bank_name, fetch_func in banks:
            try:
                count = fetch_func()
                self.total_transactions += count
                logger.info(f"✅ {bank_name}: {count} transactions")
            except Exception as e:
                logger.error(f"❌ {bank_name}: {e}")
        
        logger.info(f"Total transactions fetched: {self.total_transactions}")
    
    def schedule_fetches(self):
        """Schedule periodic fetches"""
        # Fetch every 5 minutes
        schedule.every(5).minutes.do(self.fetch_all_banks)
        
        # Run scheduler
        logger.info("Bank producer scheduler started")
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def run(self):
        logger.info("🏦 Starting Production Bank Producer...")
        self.schedule_fetches()

if __name__ == "__main__":
    producer = ProductionBankProducer()
    producer.run()
```

#### 4.2 Update Docker Compose

Add to `docker-compose.yml`:

```yaml
bank-producer:
  build: .
  container_name: bank-producer
  environment:
    - HDFC_API_TOKEN=${HDFC_API_TOKEN}
    - ICICI_API_TOKEN=${ICICI_API_TOKEN}
    - SBI_CLIENT_ID=${SBI_CLIENT_ID}
    - RAZORPAY_KEY=${RAZORPAY_KEY}
  command: python producers/production_bank_producer.py
  depends_on:
    - kafka
  networks:
    - reconciliation-network
```

#### 4.3 Start Production System

```bash
# Stop simulated producer
# Start real bank producer
docker-compose up -d bank-producer

# Monitor logs
docker logs -f bank-producer
```

---

### Phase 5: Monitoring (Ongoing)

#### 5.1 Create Monitoring Dashboard

```python
# monitoring/bank_health_monitor.py

import requests
import json
from datetime import datetime

class BankHealthMonitor:
    def __init__(self):
        self.api_url = "http://localhost:8002"
    
    def check_transaction_count(self):
        """Check transaction count by bank"""
        response = requests.get(f"{self.api_url}/api/transactions/stats")
        return response.json()
    
    def check_reconciliation_rate(self):
        """Check reconciliation success rate"""
        response = requests.get(f"{self.api_url}/api/reconciliation/stats")
        return response.json()
    
    def generate_report(self):
        """Generate health report"""
        print("\n" + "="*60)
        print("BANK RECONCILIATION HEALTH REPORT")
        print(f"Generated: {datetime.now().isoformat()}")
        print("="*60)
        
        # Transaction stats
        txn_stats = self.check_transaction_count()
        print("\n📊 Transaction Statistics:")
        for bank, count in txn_stats.items():
            print(f"  {bank}: {count} transactions")
        
        # Reconciliation stats
        recon_stats = self.check_reconciliation_rate()
        print("\n✅ Reconciliation Statistics:")
        print(f"  Success Rate: {recon_stats['success_rate']}%")
        print(f"  Total Reconciled: {recon_stats['total_reconciled']}")
        print(f"  Total Mismatches: {recon_stats['total_mismatches']}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    monitor = BankHealthMonitor()
    monitor.generate_report()
```

#### 5.2 Set Up Alerts

```python
# monitoring/alerts.py

import smtplib
from email.mime.text import MIMEText

class AlertManager:
    def __init__(self, email_config):
        self.email_config = email_config
    
    def send_alert(self, subject, message):
        """Send email alert"""
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = self.email_config['from_email']
        msg['To'] = self.email_config['to_email']
        
        with smtplib.SMTP(self.email_config['smtp_server']) as server:
            server.send_message(msg)
    
    def check_and_alert(self):
        """Check system health and send alerts"""
        # Check if any bank API is down
        # Check if reconciliation rate drops below threshold
        # Check if transaction volume is abnormal
        pass
```

---

### Troubleshooting Guide

#### Issue: API Authentication Failed
**Solution:**
1. Verify credentials in `.env` file
2. Check token expiration
3. Refresh OAuth tokens
4. Contact bank support

#### Issue: Rate Limit Exceeded
**Solution:**
1. Reduce fetch frequency
2. Implement exponential backoff
3. Request higher rate limits from bank
4. Use batch APIs if available

#### Issue: Data Format Mismatch
**Solution:**
1. Review bank's API documentation
2. Update transformation logic
3. Add data validation
4. Test with sample data

#### Issue: Network Timeout
**Solution:**
1. Increase timeout values
2. Implement retry logic
3. Check network connectivity
4. Contact bank's technical support

---

### Success Metrics

Track these metrics to ensure successful integration:

- **Transaction Volume**: Transactions fetched per hour
- **Reconciliation Rate**: % of transactions successfully reconciled
- **API Response Time**: Average API response time
- **Error Rate**: % of failed API calls
- **Data Accuracy**: % of correctly matched transactions

---

### Maintenance Checklist

- [ ] Monitor API rate limits daily
- [ ] Check reconciliation accuracy weekly
- [ ] Review error logs daily
- [ ] Update credentials before expiration
- [ ] Test failover mechanisms monthly
- [ ] Backup transaction data daily
- [ ] Review and optimize queries monthly

---

### Support Contacts

**HDFC Bank**: api-support@hdfcbank.com
**ICICI Bank**: developer@icicibank.com
**SBI**: api-support@sbi.co.in
**Razorpay**: support@razorpay.com

---

**Last Updated**: December 27, 2025
**Version**: 1.0
