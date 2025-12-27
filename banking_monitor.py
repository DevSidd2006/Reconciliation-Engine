#!/usr/bin/env python3
"""
Real-time Banking System Monitor
Displays live banking transactions and reconciliation status
"""

import time
import sys
import os
from datetime import datetime
from collections import defaultdict

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.services.real_reconciliation_service import reconciliation_engine
    from app.services.database_service import db_service
except ImportError:
    print("❌ Could not import services. Make sure backend is running.")
    sys.exit(1)

class BankingMonitor:
    def __init__(self):
        self.last_stats = {}
        self.transaction_types = defaultdict(int)
        self.currency_stats = defaultdict(int)
        self.channel_stats = defaultdict(int)
        self.bank_stats = defaultdict(int)
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_header(self):
        print("🏦" + "="*80)
        print("   REAL-TIME BANKING RECONCILIATION SYSTEM MONITOR")
        print("="*82)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Live Banking Transaction Processing")
        print("="*82)
        
    def display_reconciliation_stats(self):
        stats = reconciliation_engine.get_statistics()
        
        print("\n📊 RECONCILIATION STATISTICS")
        print("-" * 50)
        print(f"✅ Total Reconciled:     {stats['total_reconciled']:,}")
        print(f"❌ Total Mismatches:     {stats['total_mismatches']:,}")
        print(f"⏳ Pending:              {stats['pending_reconciliation']:,}")
        print(f"📈 Success Rate:         {stats['success_rate']:.1f}%")
        
        # Show rate of change
        if self.last_stats:
            reconciled_delta = stats['total_reconciled'] - self.last_stats.get('total_reconciled', 0)
            mismatch_delta = stats['total_mismatches'] - self.last_stats.get('total_mismatches', 0)
            if reconciled_delta > 0 or mismatch_delta > 0:
                print(f"🔄 Last 10s: +{reconciled_delta} reconciled, +{mismatch_delta} mismatches")
        
        self.last_stats = stats
        
    def display_recent_transactions(self):
        recent = reconciliation_engine.get_recent_reconciled(5)
        
        print("\n🔍 RECENT BANKING TRANSACTIONS")
        print("-" * 50)
        
        if not recent:
            print("⏳ Waiting for transactions...")
            return
            
        for txn in recent[-5:]:
            status_emoji = "✅" if txn['status'] == 'MATCHED' else "❌"
            sources_count = len(txn['sources'])
            
            # Get transaction details from the first source
            first_source = list(txn['transactions'].values())[0] if txn['transactions'] else {}
            amount = first_source.get('amount', 0)
            currency = first_source.get('currency', 'INR')
            txn_type = first_source.get('transaction_type', 'UNKNOWN')
            channel = first_source.get('channel', 'UNKNOWN')
            bank = first_source.get('bank_code', 'UNKNOWN')
            
            print(f"{status_emoji} {txn['txn_id'][:8]}... | ₹{amount:,.2f} {currency} | {txn_type}")
            print(f"   🏛️  {bank} via {channel} | {sources_count} sources | {txn['status']}")
            
            # Update statistics
            self.transaction_types[txn_type] += 1
            self.currency_stats[currency] += 1
            self.channel_stats[channel] += 1
            self.bank_stats[bank] += 1
            
    def display_banking_analytics(self):
        print("\n📈 BANKING ANALYTICS")
        print("-" * 50)
        
        # Transaction Types
        if self.transaction_types:
            print("💳 Transaction Types:")
            for txn_type, count in sorted(self.transaction_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {txn_type}: {count}")
                
        # Currency Distribution
        if self.currency_stats:
            print("\n💱 Currency Distribution:")
            total_currency = sum(self.currency_stats.values())
            for currency, count in sorted(self.currency_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_currency) * 100
                print(f"   {currency}: {count} ({percentage:.1f}%)")
                
        # Note: System configured for INR-only transactions
        print("\n💰 Currency Note: System configured for INR (Indian Rupees) only")
                
        # Channel Usage
        if self.channel_stats:
            print("\n📱 Channel Usage:")
            for channel, count in sorted(self.channel_stats.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"   {channel}: {count}")
                
    def display_recent_mismatches(self):
        mismatches = reconciliation_engine.detected_mismatches[-3:] if reconciliation_engine.detected_mismatches else []
        
        print("\n⚠️  RECENT MISMATCHES")
        print("-" * 50)
        
        if not mismatches:
            print("✅ No recent mismatches detected")
            return
            
        for mismatch in mismatches:
            severity_emoji = "🔴" if mismatch['severity'] == 'HIGH' else "🟡" if mismatch['severity'] == 'MEDIUM' else "🟢"
            print(f"{severity_emoji} {mismatch['type']} | {mismatch['txn_id'][:8]}...")
            print(f"   {mismatch['details']}")
            
    def run(self):
        print("🏦 Starting Banking System Monitor...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.clear_screen()
                self.display_header()
                self.display_reconciliation_stats()
                self.display_recent_transactions()
                self.display_banking_analytics()
                self.display_recent_mismatches()
                
                print("\n" + "="*82)
                print("🔄 Refreshing in 10 seconds... (Ctrl+C to stop)")
                
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n🛑 Banking monitor stopped")
            
if __name__ == "__main__":
    monitor = BankingMonitor()
    monitor.run()