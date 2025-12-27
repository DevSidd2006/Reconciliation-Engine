#!/usr/bin/env python3
"""
Banking System Status Dashboard
Comprehensive overview of the banking reconciliation system
"""

import subprocess
import json
import time
import sys
import os
from datetime import datetime

def check_docker_containers():
    """Check status of Docker containers"""
    print("🐳 DOCKER INFRASTRUCTURE STATUS")
    print("-" * 50)
    
    try:
        result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'kafka' in line.lower() or 'postgres' in line.lower() or 'zookeeper' in line.lower():
                    if 'Up' in line:
                        print(f"✅ {line}")
                    else:
                        print(f"❌ {line}")
        else:
            print("❌ Could not check Docker containers")
    except Exception as e:
        print(f"❌ Docker check failed: {e}")

def check_kafka_topics():
    """Check Kafka topics"""
    print("\n📡 KAFKA TOPICS STATUS")
    print("-" * 50)
    
    topics = ['core_txns', 'gateway_txns', 'mobile_txns']
    
    for topic in topics:
        try:
            # Check if topic exists and get message count
            cmd = ['docker', 'exec', 'kafka-kafka-1', 'kafka-run-class', 
                   'kafka.tools.GetOffsetShell', '--broker-list', 'localhost:9092', 
                   '--topic', topic, '--time', '-1']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                # Parse offset to get message count
                lines = result.stdout.strip().split('\n')
                total_messages = 0
                for line in lines:
                    if ':' in line:
                        offset = line.split(':')[-1]
                        try:
                            total_messages += int(offset)
                        except:
                            pass
                print(f"✅ {topic}: {total_messages} messages")
            else:
                print(f"⚠️  {topic}: Topic exists but no messages or error")
                
        except subprocess.TimeoutExpired:
            print(f"⏳ {topic}: Timeout checking topic")
        except Exception as e:
            print(f"❌ {topic}: Error - {e}")

def check_api_endpoints():
    """Check API endpoints"""
    print("\n🌐 API ENDPOINTS STATUS")
    print("-" * 50)
    
    import requests
    
    endpoints = [
        ('Backend Health', 'http://localhost:8002/health'),
        ('Analytics Overview', 'http://localhost:8002/api/analytics/overview'),
        ('System Health', 'http://localhost:8002/api/system/health'),
        ('Reconciliation Stats', 'http://localhost:8002/api/reconciliation/statistics'),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: {response.status_code}")
            else:
                print(f"⚠️  {name}: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Connection refused")
        except requests.exceptions.Timeout:
            print(f"⏳ {name}: Timeout")
        except Exception as e:
            print(f"❌ {name}: {e}")

def check_frontend():
    """Check frontend status"""
    print("\n🖥️  FRONTEND STATUS")
    print("-" * 50)
    
    try:
        import requests
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: Running on http://localhost:3000")
        else:
            print(f"⚠️  Frontend: Status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Frontend: Not accessible")
    except Exception as e:
        print(f"❌ Frontend: {e}")

def display_banking_system_info():
    """Display banking system information"""
    print("\n🏦 BANKING SYSTEM CONFIGURATION")
    print("-" * 50)
    print("💳 Transaction Types: TRANSFER, DEPOSIT, WITHDRAWAL, PAYMENT, REFUND, FEE, INTEREST, LOAN_PAYMENT")
    print("💱 Currency: INR (100% - Indian Rupees only)")
    print("📱 Channels: ATM, ONLINE, MOBILE, BRANCH, POS, UPI")
    print("🏛️  Banks: HDFC, ICICI, SBI, AXIS, KOTAK, PNB, BOI, CANARA")
    print("📊 Transaction Status: SUCCESS (70%), PENDING (25%), FAILED (5%)")
    print("⚠️  Mismatch Rate: 10-15% (Amount: 6%, Status: 3%, Time: 2%, Others: 4%)")

def display_access_points():
    """Display system access points"""
    print("\n🔗 SYSTEM ACCESS POINTS")
    print("-" * 50)
    print("🌐 Frontend Dashboard:    http://localhost:3000")
    print("🔧 Backend API:           http://localhost:8002")
    print("📚 API Documentation:     http://localhost:8002/docs")
    print("📊 System Health:         http://localhost:8002/api/system/health")
    print("📈 Analytics:             http://localhost:8002/api/analytics/overview")
    print("\n🔐 Login Credentials:")
    print("   Username: admin")
    print("   Password: admin123")

def main():
    """Main function"""
    print("🏦" + "="*80)
    print("   BANKING RECONCILIATION SYSTEM - COMPREHENSIVE STATUS")
    print("="*82)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | System Status Check")
    print("="*82)
    
    check_docker_containers()
    check_kafka_topics()
    check_api_endpoints()
    check_frontend()
    display_banking_system_info()
    display_access_points()
    
    print("\n" + "="*82)
    print("✅ Status check complete!")
    print("💡 Use 'python banking_monitor.py' for real-time transaction monitoring")
    print("="*82)

if __name__ == "__main__":
    main()