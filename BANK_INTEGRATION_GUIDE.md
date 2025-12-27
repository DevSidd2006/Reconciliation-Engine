# Banking Reconciliation Engine - Bank Integration Guide

## Overview
This guide explains how to connect the Reconciliation Engine with actual banking systems to process real transactions instead of simulated data.

---

## 1. Integration Architecture

### Current Architecture (Simulation)
```
Simulated Producers → Kafka Topics → Consumer → Reconciliation Engine → Database → Frontend
```

### Real Banking Architecture
```
Bank APIs/Feeds → Data Adapters → Kafka Topics → Consumer → Reconciliation Engine → Database → Frontend
```

---

## 2. Bank Data Sources

### Common Banking Data Sources

#### A. **Direct Bank APIs**
- **SWIFT/ISO 20022**: Standard banking message format
- **REST APIs**: Modern bank APIs (HDFC, ICICI, Axis, SBI)
- **SFTP/File Transfer**: Batch transaction files
- **Database Replication**: Direct database connections

#### B. **Payment Gateways**
- **Razorpay API**
- **PayU API**
- **Instamojo API**
- **CCAvenue API**

#### C. **Banking Networks**
- **NPCI (National Payments Corporation of India)**
- **RBI Systems**
- **NEFT/RTGS Systems**
- **UPI Network**

---

## 3. Integration Steps

### Step 1: Create Bank Data Adapters

Replace the simulated producer with actual bank connectors:

```python
# File: producers/bank_adapter.py

import requests
import json
from datetime import datetime
from kafka import KafkaProducer

class BankDataAdapter:
    """Adapter to fetch real transaction data from banks"""
    
    def __init__(self, bank_config):
        self.bank_config = bank_config
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def fetch_from_hdfc_api(self):
        """Fetch transactions from HDFC Bank API"""
        headers = {
            'Authorization': f'Bearer {self.bank_config["hdfc_token"]}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://api.hdfcbank.com/v1/transactions',
            headers=headers,
            params={
                'from_date': datetime.now().isoformat(),
                'to_date': datetime.now().isoformat(),
                'limit': 100
            }
        )
        
        if response.status_code == 200:
            transactions = response.json()['data']
            for txn in transactions:
                self.send_to_kafka(txn, 'hdfc_txns')
    
    def fetch_from_icici_api(self):
        """Fetch transactions from ICICI Bank API"""
        headers = {
            'Authorization': f'Bearer {self.bank_config["icici_token"]}',
            'X-API-Key': self.bank_config["icici_api_key"]
        }
        
        response = requests.get(
            'https://api.icicibank.com/v2/transactions',
            headers=headers
        )
        
        if response.status_code == 200:
            transactions = response.json()['transactions']
            for txn in transactions:
                self.send_to_kafka(txn, 'icici_txns')
    
    def fetch_from_sbi_api(self):
        """Fetch transactions from SBI API"""
        # SBI uses OAuth 2.0
        auth_token = self.get_sbi_oauth_token()
        
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Accept': 'application/json'
        }
        
        response = requests.get(
            'https://api.sbi.co.in/api/v1/transactions',
            headers=headers
        )
        
        if response.status_code == 200:
            transactions = response.json()['data']
            for txn in transactions:
                self.send_to_kafka(txn, 'sbi_txns')
    
    def fetch_from_razorpay(self):
        """Fetch transactions from Razorpay"""
        auth = (self.bank_config["razorpay_key"], self.bank_config["razorpay_secret"])
        
        response = requests.get(
            'https://api.razorpay.com/v1/payments',
            auth=auth,
            params={'count': 100}
        )
        
        if response.status_code == 200:
            payments = response.json()['items']
            for payment in payments:
                txn = self.transform_razorpay_payment(payment)
                self.send_to_kafka(txn, 'razorpay_txns')
    
    def fetch_from_sftp(self, bank_name):
        """Fetch transaction files from SFTP"""
        import paramiko
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            self.bank_config[f'{bank_name}_sftp_host'],
            username=self.bank_config[f'{bank_name}_sftp_user'],
            password=self.bank_config[f'{bank_name}_sftp_password']
        )
        
        sftp = ssh.open_sftp()
        files = sftp.listdir(f'/transactions/{bank_name}/')
        
        for file in files:
            with sftp.file(f'/transactions/{bank_name}/{file}', 'r') as f:
                transactions = json.load(f)
                for txn in transactions:
                    self.send_to_kafka(txn, f'{bank_name}_txns')
        
        sftp.close()
        ssh.close()
    
    def send_to_kafka(self, transaction, topic):
        """Send transaction to Kafka topic"""
        self.producer.send(topic, value=transaction)
        self.producer.flush()
    
    def transform_razorpay_payment(self, payment):
        """Transform Razorpay payment to standard format"""
        return {
            'txn_id': payment['id'],
            'amount': payment['amount'] / 100,  # Convert paise to rupees
            'currency': payment['currency'],
            'status': payment['status'].upper(),
            'timestamp': datetime.fromtimestamp(payment['created_at']).isoformat(),
            'account_id': payment['customer_id'],
            'source': 'razorpay',
            'bank_code': 'RAZORPAY',
            'channel': 'ONLINE',
            'transaction_type': 'PAYMENT',
            'reference_number': payment['receipt']
        }
    
    def get_sbi_oauth_token(self):
        """Get OAuth token from SBI"""
        response = requests.post(
            'https://api.sbi.co.in/oauth/token',
            data={
                'grant_type': 'client_credentials',
                'client_id': self.bank_config['sbi_client_id'],
                'client_secret': self.bank_config['sbi_client_secret']
            }
        )
        return response.json()['access_token']
```

### Step 2: Update Configuration

Create a bank configuration file:

```python
# File: config/bank_config.py

BANK_CONFIG = {
    # HDFC Bank
    'hdfc_token': 'your_hdfc_api_token',
    'hdfc_api_url': 'https://api.hdfcbank.com',
    
    # ICICI Bank
    'icici_token': 'your_icici_api_token',
    'icici_api_key': 'your_icici_api_key',
    'icici_api_url': 'https://api.icicibank.com',
    
    # SBI
    'sbi_client_id': 'your_sbi_client_id',
    'sbi_client_secret': 'your_sbi_client_secret',
    'sbi_api_url': 'https://api.sbi.co.in',
    
    # Razorpay
    'razorpay_key': 'your_razorpay_key',
    'razorpay_secret': 'your_razorpay_secret',
    
    # SFTP Connections
    'axis_sftp_host': 'sftp.axisbank.com',
    'axis_sftp_user': 'your_username',
    'axis_sftp_password': 'your_password',
    
    'kotak_sftp_host': 'sftp.kotakbank.com',
    'kotak_sftp_user': 'your_username',
    'kotak_sftp_password': 'your_password',
}

# Kafka Topics for each bank
KAFKA_TOPICS = {
    'hdfc': 'hdfc_txns',
    'icici': 'icici_txns',
    'sbi': 'sbi_txns',
    'axis': 'axis_txns',
    'kotak': 'kotak_txns',
    'razorpay': 'razorpay_txns',
}
```

### Step 3: Create Multi-Bank Producer

```python
# File: producers/multi_bank_producer.py

import time
import schedule
from bank_adapter import BankDataAdapter
from config.bank_config import BANK_CONFIG

class MultiBankProducer:
    """Fetch transactions from multiple banks"""
    
    def __init__(self):
        self.adapter = BankDataAdapter(BANK_CONFIG)
    
    def fetch_all_banks(self):
        """Fetch from all configured banks"""
        print("Fetching transactions from all banks...")
        
        try:
            self.adapter.fetch_from_hdfc_api()
            print("✅ HDFC transactions fetched")
        except Exception as e:
            print(f"❌ HDFC error: {e}")
        
        try:
            self.adapter.fetch_from_icici_api()
            print("✅ ICICI transactions fetched")
        except Exception as e:
            print(f"❌ ICICI error: {e}")
        
        try:
            self.adapter.fetch_from_sbi_api()
            print("✅ SBI transactions fetched")
        except Exception as e:
            print(f"❌ SBI error: {e}")
        
        try:
            self.adapter.fetch_from_razorpay()
            print("✅ Razorpay transactions fetched")
        except Exception as e:
            print(f"❌ Razorpay error: {e}")
        
        try:
            self.adapter.fetch_from_sftp('axis')
            print("✅ Axis transactions fetched")
        except Exception as e:
            print(f"❌ Axis error: {e}")
    
    def schedule_fetches(self):
        """Schedule periodic fetches"""
        # Fetch every 5 minutes
        schedule.every(5).minutes.do(self.fetch_all_banks)
        
        # Fetch every hour for batch files
        schedule.every(1).hours.do(self.adapter.fetch_from_sftp, 'kotak')
        
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def run(self):
        """Run the multi-bank producer"""
        print("🏦 Starting Multi-Bank Transaction Producer...")
        print("Connecting to real banking systems...")
        self.schedule_fetches()

if __name__ == "__main__":
    producer = MultiBankProducer()
    producer.run()
```

### Step 4: Update Consumer for Real Data

```python
# File: backend/app/consumers/bank_reconciliation_consumer.py

import json
import logging
from kafka import KafkaConsumer
from app.services.real_reconciliation_service import reconciliation_engine
from app.services.database_service import db_service

logger = logging.getLogger(__name__)

class BankReconciliationConsumer:
    """Consume real bank transactions"""
    
    def __init__(self):
        self.consumer = KafkaConsumer(
            'hdfc_txns', 'icici_txns', 'sbi_txns', 'axis_txns', 
            'kotak_txns', 'razorpay_txns',
            bootstrap_servers=['localhost:9092'],
            group_id='bank-reconciliation-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest'
        )
    
    def process_transaction(self, transaction):
        """Process real bank transaction"""
        try:
            # Validate transaction
            if not self.validate_transaction(transaction):
                logger.warning(f"Invalid transaction: {transaction}")
                return
            
            # Save to database
            db_service.save_transaction(transaction)
            
            # Add to reconciliation engine
            reconciliation_engine.add_transaction(transaction)
            
            logger.info(f"Processed: {transaction['txn_id']} from {transaction['source']}")
            
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
    
    def validate_transaction(self, txn):
        """Validate transaction data"""
        required_fields = ['txn_id', 'amount', 'status', 'timestamp', 'source']
        return all(field in txn for field in required_fields)
    
    def run(self):
        """Run the consumer"""
        logger.info("Starting Bank Reconciliation Consumer...")
        
        for message in self.consumer:
            transaction = message.value
            self.process_transaction(transaction)

if __name__ == "__main__":
    consumer = BankReconciliationConsumer()
    consumer.run()
```

---

## 4. Bank-Specific Integration Details

### HDFC Bank
- **API Endpoint**: `https://api.hdfcbank.com`
- **Authentication**: OAuth 2.0
- **Rate Limit**: 1000 requests/hour
- **Documentation**: https://developer.hdfcbank.com

### ICICI Bank
- **API Endpoint**: `https://api.icicibank.com`
- **Authentication**: API Key + Bearer Token
- **Rate Limit**: 500 requests/hour
- **Documentation**: https://developer.icicibank.com

### SBI (State Bank of India)
- **API Endpoint**: `https://api.sbi.co.in`
- **Authentication**: OAuth 2.0
- **Rate Limit**: 2000 requests/hour
- **Documentation**: https://developer.sbi.co.in

### Axis Bank
- **Method**: SFTP File Transfer
- **File Format**: CSV/JSON
- **Frequency**: Daily/Hourly
- **Contact**: api-support@axisbank.com

### Razorpay (Payment Gateway)
- **API Endpoint**: `https://api.razorpay.com`
- **Authentication**: Basic Auth (Key + Secret)
- **Rate Limit**: Unlimited
- **Documentation**: https://razorpay.com/docs/api

---

## 5. Data Transformation

### Standard Transaction Format

```json
{
  "txn_id": "TXN123456789",
  "amount": 5000.00,
  "currency": "INR",
  "status": "SUCCESS",
  "timestamp": "2025-12-27T14:30:00Z",
  "account_id": "123456789",
  "source": "hdfc",
  "bank_code": "HDFC",
  "channel": "UPI",
  "transaction_type": "TRANSFER",
  "reference_number": "REF123456",
  "merchant_id": "MER12345",
  "description": "Payment for services"
}
```

---

## 6. Security Considerations

### API Key Management
```python
# Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()

HDFC_API_KEY = os.getenv('HDFC_API_KEY')
ICICI_API_KEY = os.getenv('ICICI_API_KEY')
SBI_CLIENT_ID = os.getenv('SBI_CLIENT_ID')
```

### Encryption
```python
from cryptography.fernet import Fernet

# Encrypt sensitive data
cipher = Fernet(os.getenv('ENCRYPTION_KEY'))
encrypted_token = cipher.encrypt(api_token.encode())
```

### SSL/TLS
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
```

---

## 7. Error Handling & Retry Logic

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=5):
    """Decorator for retry logic"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed: {e}")
                        raise
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=5)
def fetch_bank_transactions():
    # Your bank API call here
    pass
```

---

## 8. Monitoring & Logging

```python
import logging
from logging.handlers import RotatingFileHandler

# Setup logging
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('bank_integration.log', maxBytes=10485760, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Log important events
logger.info(f"Fetched {count} transactions from {bank_name}")
logger.warning(f"API rate limit approaching: {remaining_requests} requests left")
logger.error(f"Failed to connect to {bank_name}: {error_message}")
```

---

## 9. Deployment Steps

### Step 1: Get Bank API Credentials
- Contact each bank's developer support
- Register your application
- Get API keys and credentials
- Set up IP whitelisting

### Step 2: Configure Environment
```bash
# .env file
HDFC_API_KEY=your_key
HDFC_API_SECRET=your_secret
ICICI_API_KEY=your_key
SBI_CLIENT_ID=your_id
SBI_CLIENT_SECRET=your_secret
RAZORPAY_KEY=your_key
RAZORPAY_SECRET=your_secret
```

### Step 3: Replace Producer
```bash
# Stop simulated producer
# Start real bank producer
python producers/multi_bank_producer.py
```

### Step 4: Update Consumer
```bash
# Update consumer to use real bank topics
python backend/app/consumers/bank_reconciliation_consumer.py
```

### Step 5: Monitor & Test
- Check Kafka topics for real transactions
- Verify reconciliation accuracy
- Monitor error logs
- Test with small transaction volumes first

---

## 10. Testing Checklist

- [ ] API credentials configured correctly
- [ ] SSL/TLS certificates valid
- [ ] Kafka topics created for each bank
- [ ] Consumer successfully reading real transactions
- [ ] Reconciliation engine processing real data
- [ ] Database storing transactions correctly
- [ ] Frontend displaying real transaction data
- [ ] Error handling working properly
- [ ] Logging capturing all events
- [ ] Performance acceptable with real data volume

---

## 11. Support & Troubleshooting

### Common Issues

**Issue**: API Authentication Failed
- **Solution**: Verify credentials, check token expiration, refresh OAuth tokens

**Issue**: Rate Limit Exceeded
- **Solution**: Implement exponential backoff, reduce fetch frequency

**Issue**: Data Format Mismatch
- **Solution**: Update transformation logic, validate against bank's schema

**Issue**: Network Timeout
- **Solution**: Increase timeout values, implement retry logic

---

## 12. Next Steps

1. **Contact Banks**: Reach out to developer support for API access
2. **Get Credentials**: Obtain API keys and authentication details
3. **Test Integration**: Start with sandbox/test environments
4. **Deploy**: Move to production with real transaction data
5. **Monitor**: Continuously monitor reconciliation accuracy

---

## Contact & Support

For integration support:
- Bank API Documentation: Check each bank's developer portal
- Reconciliation Engine Issues: Check GitHub issues
- General Questions: Contact your bank's technical support team

---

**Last Updated**: December 27, 2025
**Version**: 1.0
