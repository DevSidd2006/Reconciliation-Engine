#!/usr/bin/env python3
"""
Real-time Dashboard Monitor
Shows live transaction statistics as they update
"""
import requests
import time
import json
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8002"
USERNAME = "admin"
PASSWORD = "admin123"

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={
            "username": USERNAME,
            "password": PASSWORD
        })
        return response.json()["access_token"]
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None

def get_stats(token):
    """Get current statistics"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get overview stats
        overview = requests.get(f"{API_BASE}/api/analytics/overview", headers=headers)
        stats = requests.get(f"{API_BASE}/api/stats", headers=headers)
        
        return overview.json(), stats.json()
    except Exception as e:
        print(f"❌ Failed to fetch stats: {e}")
        return None, None

def display_stats(overview, stats):
    """Display formatted statistics"""
    print("\n" + "="*80)
    print(f"🏦 BANKING RECONCILIATION DASHBOARD - {datetime.now().strftime('%H:%M:%S')}")
    print("="*80)
    
    if overview and stats:
        kpis = overview.get('kpis', {})
        
        print(f"📊 TODAY'S TRANSACTIONS: {kpis.get('total_transactions_today', 0):,}")
        print(f"🚨 TOTAL MISMATCHES: {kpis.get('total_mismatches', 0):,}")
        print(f"🎯 RECONCILIATION ACCURACY: {kpis.get('reconciliation_accuracy', 0)}%")
        print(f"⏳ PENDING TRANSACTIONS: {kpis.get('pending_transactions', 0):,}")
        print(f"🔄 DUPLICATES DETECTED: {kpis.get('duplicates_detected', 0):,}")
        print(f"⏰ DELAYED TRANSACTIONS: {kpis.get('delayed_transactions', 0):,}")
        
        print("\n📈 SOURCE DISTRIBUTION:")
        source_dist = stats.get('source_distribution', {})
        for source, count in source_dist.items():
            print(f"   {source.upper()}: {count:,}")
        
        print("\n🚨 MISMATCH TYPES:")
        mismatch_types = stats.get('mismatch_types', {})
        for mtype, count in mismatch_types.items():
            print(f"   {mtype}: {count:,}")
        
        print(f"\n📊 TOTAL TRANSACTIONS: {stats.get('total_transactions', 0):,}")
        print(f"✅ SUCCESS RATE: {stats.get('success_rate', 0)}%")
        
    else:
        print("❌ Unable to fetch statistics")

def main():
    """Main monitoring loop"""
    print("🚀 Starting Real-time Dashboard Monitor...")
    print("Press Ctrl+C to stop\n")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        return
    
    print("✅ Authentication successful!")
    
    try:
        while True:
            overview, stats = get_stats(token)
            display_stats(overview, stats)
            
            print(f"\n⏳ Next update in 15 seconds...")
            time.sleep(15)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor stopped")

if __name__ == "__main__":
    main()