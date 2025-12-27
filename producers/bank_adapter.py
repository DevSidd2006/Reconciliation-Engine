"""
Bank Data Adapter - Fetch real transactions from banking systems
"""

import requests
import json
import logging
from datetime import datetime
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BankDataAdapter:
    """Adapter to fetch real transaction data from banks"""
    
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Load credentials from environment
        self.hdfc_token = os.getenv('HDFC_API_TOKEN')
        self.icici_token = os.getenv('ICICI_API_TOKEN')
        self.icici_api_key = os.getenv('ICICI_API_KEY')
        self.sbi_client_id = os.getenv('SBI_CLIENT_ID')
        self.sbi_client_secret = os.getenv('SBI_CLIENT_SECRET')
        self.razorpay_key = os.getenv('RAZORPAY_KEY')
        self.razorpay_secret = os.getenv('RAZORPAY_SECRET')
    
    def fetch_from_hdfc_api(self):
        """Fetch transactions from HDFC Bank API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.hdfc_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://api.hdfcbank.com/v1/transactions',
                headers=headers,
                params={
                    'limit': 100,
                    'offset': 0
                },
                timeout=10
            )
            
            if response.status_code == 200:
                transactions = response.json().get('data', [])
                count = 0
                for txn in transactions:
                    standardized_txn = self.standardize_hdfc_transaction(txn)
                    self.send_to_kafka(standardized_txn, 'hdfc_txns')
                    count += 1
                logger.info(f"✅ Fetched {count} transactions from HDFC")
                return count
            else:
                logger.error(f"HDFC API error: {response.status_code} - {response.text}")
                return 0
                
        except Exception as e:
            logger.error(f"❌ HDFC fetch error: {e}")
            return 0
    
    def fetch_from_icici_api(self):
        """Fetch transactions from ICICI Bank API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.icici_token}',
                'X-API-Key': self.icici_api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://api.icicibank.com/v2/transactions',
                headers=headers,
                params={'limit': 100},
                timeout=10
            )
            
            if response.status_code == 200:
                transactions = response.json().get('transactions', [])
                count = 0
                for txn in transactions:
                    standardized_txn = self.standardize_icici_transaction(txn)
                    self.send_to_kafka(standardized_txn, 'icici_txns')
                    count += 1
                logger.info(f"✅ Fetched {count} transactions from ICICI")
                return count
            else:
                logger.error(f"ICICI API error: {response.status_code}")
                return 0
                
        except Exception as e:
            logger.error(f"❌ ICICI fetch error: {e}")
            return 0
    
    def fetch_from_sbi_api(self):
        """Fetch transactions from SBI API"""
        try:
            # Get OAuth token
            auth_token = self.get_sbi_oauth_token()
            if not auth_token:
                logger.error("Failed to get SBI OAuth token")
                return 0
            
            headers = {
                'Authorization': f'Bearer {auth_token}',
                'Accept': 'application/json'
            }
            
            response = requests.get(
                'https://api.sbi.co.in/api/v1/transactions',
                headers=headers,
                params={'limit': 100},
                timeout=10
            )
            
            if response.status_code == 200:
                transactions = response.json().get('data', [])
                count = 0
                for txn in transactions:
                    standardized_txn = self.standardize_sbi_transaction(txn)
                    self.send_to_kafka(standardized_txn, 'sbi_txns')
                    count += 1
                logger.info(f"✅ Fetched {count} transactions from SBI")
                return count
            else:
                logger.error(f"SBI API error: {response.status_code}")
                return 0
                
        except Exception as e:
            logger.error(f"❌ SBI fetch error: {e}")
            return 0
    
    def fetch_from_razorpay(self):
        """Fetch transactions from Razorpay"""
        try:
            auth = (self.razorpay_key, self.razorpay_secret)
            
            response = requests.get(
                'https://api.razorpay.com/v1/payments',
                auth=auth,
                params={'count': 100},
                timeout=10
            )
            
            if response.status_code == 200:
                payments = response.json().get('items', [])
                count = 0
                for payment in payments:
                    standardized_txn = self.standardize_razorpay_payment(payment)
                    self.send_to_kafka(standardized_txn, 'razorpay_txns')
                    count += 1
                logger.info(f"✅ Fetched {count} transactions from Razorpay")
                return count
            else:
                logger.error(f"Razorpay API error: {response.status_code}")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Razorpay fetch error: {e}")
            return 0
    
    def send_to_kafka(self, transaction, topic):
        """Send transaction to Kafka topic"""
        try:
            self.producer.send(topic, value=transaction)
            self.producer.flush()
        except Exception as e:
            logger.error(f"Failed to send to Kafka: {e}")
    
    def standardize_hdfc_transaction(self, txn):
        """Transform HDFC transaction to standard format"""
        return {
            'txn_id': txn.get('transaction_id'),
            'amount': float(txn.get('amount', 0)),
            'currency': txn.get('currency', 'INR'),
            'status': txn.get('status', 'PENDING').upper(),
            'timestamp': txn.get('transaction_date', datetime.now().isoformat()),
            'account_id': txn.get('account_number'),
            'source': 'hdfc',
            'bank_code': 'HDFC',
            'channel': txn.get('channel', 'ONLINE').upper(),
            'transaction_type': txn.get('type', 'TRANSFER').upper(),
            'reference_number': txn.get('reference_id'),
            'description': txn.get('description', '')
        }
    
    def standardize_icici_transaction(self, txn):
        """Transform ICICI transaction to standard format"""
        return {
            'txn_id': txn.get('txn_id'),
            'amount': float(txn.get('amount', 0)),
            'currency': txn.get('currency', 'INR'),
            'status': txn.get('status', 'PENDING').upper(),
            'timestamp': txn.get('timestamp', datetime.now().isoformat()),
            'account_id': txn.get('account_id'),
            'source': 'icici',
            'bank_code': 'ICICI',
            'channel': txn.get('channel', 'ONLINE').upper(),
            'transaction_type': txn.get('type', 'TRANSFER').upper(),
            'reference_number': txn.get('ref_no'),
            'description': txn.get('remarks', '')
        }
    
    def standardize_sbi_transaction(self, txn):
        """Transform SBI transaction to standard format"""
        return {
            'txn_id': txn.get('transaction_id'),
            'amount': float(txn.get('amount', 0)),
            'currency': txn.get('currency', 'INR'),
            'status': txn.get('status', 'PENDING').upper(),
            'timestamp': txn.get('value_date', datetime.now().isoformat()),
            'account_id': txn.get('account_number'),
            'source': 'sbi',
            'bank_code': 'SBI',
            'channel': txn.get('channel', 'ONLINE').upper(),
            'transaction_type': txn.get('transaction_type', 'TRANSFER').upper(),
            'reference_number': txn.get('reference_number'),
            'description': txn.get('description', '')
        }
    
    def standardize_razorpay_payment(self, payment):
        """Transform Razorpay payment to standard format"""
        return {
            'txn_id': payment.get('id'),
            'amount': float(payment.get('amount', 0)) / 100,  # Convert paise to rupees
            'currency': payment.get('currency', 'INR'),
            'status': payment.get('status', 'PENDING').upper(),
            'timestamp': datetime.fromtimestamp(payment.get('created_at', 0)).isoformat(),
            'account_id': payment.get('customer_id'),
            'source': 'razorpay',
            'bank_code': 'RAZORPAY',
            'channel': 'ONLINE',
            'transaction_type': 'PAYMENT',
            'reference_number': payment.get('receipt'),
            'description': payment.get('description', '')
        }
    
    def get_sbi_oauth_token(self):
        """Get OAuth token from SBI"""
        try:
            response = requests.post(
                'https://api.sbi.co.in/oauth/token',
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.sbi_client_id,
                    'client_secret': self.sbi_client_secret
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                logger.error(f"SBI OAuth error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"SBI OAuth fetch error: {e}")
            return None


if __name__ == "__main__":
    adapter = BankDataAdapter()
    
    print("Testing Bank Data Adapter...")
    print("Note: Configure environment variables with real bank credentials first")
    print("\nRequired environment variables:")
    print("- HDFC_API_TOKEN")
    print("- ICICI_API_TOKEN")
    print("- ICICI_API_KEY")
    print("- SBI_CLIENT_ID")
    print("- SBI_CLIENT_SECRET")
    print("- RAZORPAY_KEY")
    print("- RAZORPAY_SECRET")
