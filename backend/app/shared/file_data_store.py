"""
File-based data store for sharing reconciliation data between processes
"""
import json
import os
import threading
import time
from typing import Dict, List
from collections import defaultdict

class FileDataStore:
    def __init__(self, data_file="reconciliation_data.json"):
        self.data_file = os.path.join(os.path.dirname(__file__), data_file)
        self.lock = threading.Lock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the data file exists with initial structure"""
        if not os.path.exists(self.data_file):
            initial_data = {
                "reconciled_transactions": [],
                "detected_mismatches": [],
                "statistics": {
                    "total_reconciled": 0,
                    "total_mismatches": 0,
                    "success_rate": 100,
                    "pending_reconciliation": 0,
                    "mismatch_types": {},
                    "source_counts": {}
                },
                "last_updated": time.time()
            }
            self._write_data(initial_data)
    
    def _read_data(self):
        """Read data from file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._ensure_file_exists()
            with open(self.data_file, 'r') as f:
                return json.load(f)
    
    def _write_data(self, data):
        """Write data to file"""
        data["last_updated"] = time.time()
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_reconciled_transaction(self, transaction_data):
        """Add a reconciled transaction"""
        with self.lock:
            data = self._read_data()
            data["reconciled_transactions"].append(transaction_data)
            
            # Keep only last 100 transactions
            if len(data["reconciled_transactions"]) > 100:
                data["reconciled_transactions"] = data["reconciled_transactions"][-100:]
            
            self._update_statistics(data)
            self._write_data(data)
    
    def add_mismatch(self, mismatch_data):
        """Add a detected mismatch"""
        with self.lock:
            data = self._read_data()
            data["detected_mismatches"].append(mismatch_data)
            
            # Keep only last 50 mismatches
            if len(data["detected_mismatches"]) > 50:
                data["detected_mismatches"] = data["detected_mismatches"][-50:]
            
            self._update_statistics(data)
            self._write_data(data)
    
    def _update_statistics(self, data):
        """Update statistics based on current data"""
        reconciled = data["reconciled_transactions"]
        mismatches = data["detected_mismatches"]
        
        total_reconciled = len(reconciled)
        total_mismatches = len([r for r in reconciled if r.get('status') == 'MISMATCH'])
        success_rate = ((total_reconciled - total_mismatches) / total_reconciled * 100) if total_reconciled > 0 else 100
        
        # Count by mismatch type
        mismatch_types = defaultdict(int)
        for mismatch in mismatches:
            mismatch_types[mismatch['type']] += 1
        
        # Count by source (approximate from recent transactions)
        source_counts = defaultdict(int)
        for txn in reconciled[-20:]:  # Last 20 transactions
            for source in txn.get('sources', []):
                source_counts[source] += 1
        
        data["statistics"] = {
            "total_reconciled": total_reconciled,
            "total_mismatches": total_mismatches,
            "success_rate": round(success_rate, 1),
            "pending_reconciliation": 0,  # We'll update this separately
            "mismatch_types": dict(mismatch_types),
            "source_counts": dict(source_counts)
        }
    
    def get_reconciled_transactions(self, limit=50):
        """Get recent reconciled transactions"""
        data = self._read_data()
        transactions = data["reconciled_transactions"]
        return transactions[-limit:] if transactions else []
    
    def get_mismatches(self, limit=20):
        """Get recent mismatches"""
        data = self._read_data()
        mismatches = data["detected_mismatches"]
        return mismatches[-limit:] if mismatches else []
    
    def get_statistics(self):
        """Get reconciliation statistics"""
        data = self._read_data()
        return data["statistics"]

# Global file-based data store
file_data_store = FileDataStore()