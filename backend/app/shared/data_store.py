"""
Shared data store for reconciliation data
This allows the consumer and API to share the same data
"""
import threading
from typing import Dict, List
from collections import defaultdict

class SharedDataStore:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.reconciled_transactions = []
        self.detected_mismatches = []
        self.pending_transactions = defaultdict(dict)
        self.data_lock = threading.Lock()
        self._initialized = True
    
    def add_reconciled_transaction(self, transaction_data):
        """Add a reconciled transaction"""
        with self.data_lock:
            self.reconciled_transactions.append(transaction_data)
            # Keep only last 100 reconciled transactions
            if len(self.reconciled_transactions) > 100:
                self.reconciled_transactions = self.reconciled_transactions[-100:]
    
    def add_mismatch(self, mismatch_data):
        """Add a detected mismatch"""
        with self.data_lock:
            self.detected_mismatches.append(mismatch_data)
            # Keep only last 50 mismatches
            if len(self.detected_mismatches) > 50:
                self.detected_mismatches = self.detected_mismatches[-50:]
    
    def update_pending(self, pending_data):
        """Update pending transactions"""
        with self.data_lock:
            self.pending_transactions = pending_data.copy()
    
    def get_reconciled_transactions(self, limit=50):
        """Get recent reconciled transactions"""
        with self.data_lock:
            return self.reconciled_transactions[-limit:] if self.reconciled_transactions else []
    
    def get_mismatches(self, limit=20):
        """Get recent mismatches"""
        with self.data_lock:
            return self.detected_mismatches[-limit:] if self.detected_mismatches else []
    
    def get_statistics(self):
        """Get reconciliation statistics"""
        with self.data_lock:
            total_reconciled = len(self.reconciled_transactions)
            total_mismatches = len([r for r in self.reconciled_transactions if r.get('status') == 'MISMATCH'])
            success_rate = ((total_reconciled - total_mismatches) / total_reconciled * 100) if total_reconciled > 0 else 100
            
            # Count by mismatch type
            mismatch_types = defaultdict(int)
            for mismatch in self.detected_mismatches:
                mismatch_types[mismatch['type']] += 1
            
            # Count by source
            source_counts = defaultdict(int)
            for txn_id, sources in self.pending_transactions.items():
                for source in sources.keys():
                    source_counts[source] += 1
            
            return {
                'total_reconciled': total_reconciled,
                'total_mismatches': total_mismatches,
                'success_rate': round(success_rate, 1),
                'pending_reconciliation': len(self.pending_transactions),
                'mismatch_types': dict(mismatch_types),
                'source_counts': dict(source_counts)
            }

# Global shared instance
shared_data = SharedDataStore()