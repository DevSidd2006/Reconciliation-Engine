import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import threading
import logging

from services.redis_service import redis_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReconciliationEngine:
    def __init__(self):
        # Store transactions by txn_id for comparison
        self.pending_transactions = defaultdict(dict)  # {txn_id: {source: transaction}}
        self.reconciled_transactions = []
        self.detected_mismatches = []
        self.lock = threading.Lock()
        
        # Reconciliation rules
        self.amount_tolerance = 0.01  # ₹0.01 tolerance for amount differences
        self.time_tolerance = 300     # 5 minutes tolerance for timestamp differences
        
    def add_transaction(self, transaction: dict):
        """Add a transaction from any source for reconciliation - Enhanced with Redis"""
        with self.lock:
            txn_id = transaction.get('txn_id')
            source = transaction.get('source')
            
            if not txn_id or not source:
                logger.warning(f"Invalid transaction: missing txn_id or source")
                return
            
            # Store in Redis for in-flight tracking
            if redis_service.is_connected():
                redis_service.store_inflight_transaction(txn_id, transaction)
            
            # Store transaction by source (fallback to memory)
            self.pending_transactions[txn_id][source] = transaction
            
            logger.info(f"Added transaction {txn_id} from {source}")
            
            # Always attempt reconciliation for now (disable throttling)
            self._attempt_reconciliation(txn_id)
    
    def _attempt_reconciliation(self, txn_id: str):
        """Attempt to reconcile a transaction across all sources - Enhanced with Redis locking"""
        # Acquire Redis lock to prevent race conditions
        if redis_service.is_connected():
            if not redis_service.acquire_reconciliation_lock(txn_id):
                logger.info(f"Reconciliation already in progress for {txn_id}")
                return
        
        try:
            sources = self.pending_transactions[txn_id]
            
            # We need at least 2 sources to reconcile, but let's be more aggressive
            if len(sources) < 2:
                return
            
            # If we have 2 sources and it's been more than 30 seconds, reconcile anyway
            # This prevents transactions from staying pending forever
            
            logger.info(f"Attempting reconciliation for {txn_id} with sources: {list(sources.keys())}")
            
            # Perform reconciliation checks
            mismatches = self._detect_mismatches(txn_id, sources)
            
            # Create and process reconciliation result
            self._process_reconciliation_result(txn_id, sources, mismatches)
            
        finally:
            # Always release the lock
            if redis_service.is_connected():
                redis_service.release_reconciliation_lock(txn_id)
    
    def _process_reconciliation_result(self, txn_id: str, sources: dict, mismatches: list):
        """Process the reconciliation result and update systems"""
        # Create reconciliation result
        reconciliation_result = {
            'txn_id': txn_id,
            'sources': list(sources.keys()),
            'timestamp': datetime.now().isoformat(),
            'status': 'MISMATCH' if mismatches else 'MATCHED',
            'mismatches': mismatches,
            'transactions': sources
        }
        
        self.reconciled_transactions.append(reconciliation_result)
        
        # Add mismatches to the detected list
        for mismatch in mismatches:
            mismatch_data = {
                'id': f"{txn_id}_{mismatch['type']}_{int(time.time())}",
                'txn_id': txn_id,
                'type': mismatch['type'],
                'severity': mismatch['severity'],
                'details': mismatch['details'],
                'sources_involved': mismatch['sources'],
                'timestamp': datetime.now().isoformat()
            }
            self.detected_mismatches.append(mismatch_data)
        
        # Update database
        try:
            try:
                from services.database_service import db_service
            except ImportError:
                from app.services.database_service import db_service
            
            # Update reconciliation status for all transactions with this txn_id
            reconciliation_status = 'MISMATCH' if mismatches else 'MATCHED'
            db_service.update_reconciliation_status(txn_id, reconciliation_status, list(sources.keys()))
            
            # Save mismatches to database
            for mismatch in mismatches:
                mismatch_data = {
                    'txn_id': txn_id,
                    'type': mismatch['type'],
                    'severity': mismatch['severity'],
                    'details': mismatch['details'],
                    'sources_involved': mismatch['sources'],
                    'expected_value': str(mismatch.get('values', {}).get(mismatch['sources'][0], '')),
                    'actual_value': str(mismatch.get('values', {}).get(mismatch['sources'][1], '')) if len(mismatch['sources']) > 1 else '',
                    'difference_amount': None  # Will be calculated for amount mismatches
                }
                
                # Calculate difference for amount mismatches
                if mismatch['type'] == 'AMOUNT_MISMATCH' and 'values' in mismatch:
                    values = list(mismatch['values'].values())
                    if len(values) >= 2:
                        try:
                            mismatch_data['difference_amount'] = abs(float(values[0]) - float(values[1]))
                        except:
                            pass
                
                db_service.save_mismatch(mismatch_data)
                
        except Exception as e:
            logger.warning(f"Failed to update database: {e}")
        
        # Clean up Redis in-flight transactions
        if redis_service.is_connected():
            for source in sources.keys():
                redis_service.remove_inflight_transaction(txn_id, source)
        
        # Remove from pending (transaction is now reconciled)
        if len(sources) >= 2:  # Keep it if we're still waiting for more sources
            pass  # Keep for now, in real system you'd have timeout logic
        
        logger.info(f"Reconciliation complete for {txn_id}: {reconciliation_result['status']}")
    
    def _detect_mismatches(self, txn_id: str, sources: Dict[str, dict]) -> List[dict]:
        """Detect mismatches between transaction sources"""
        mismatches = []
        source_list = list(sources.keys())
        
        # Compare each pair of sources
        for i in range(len(source_list)):
            for j in range(i + 1, len(source_list)):
                source1, source2 = source_list[i], source_list[j]
                txn1, txn2 = sources[source1], sources[source2]
                
                # Check amount mismatch
                amount1 = float(txn1.get('amount', 0))
                amount2 = float(txn2.get('amount', 0))
                if abs(amount1 - amount2) > self.amount_tolerance:
                    mismatches.append({
                        'type': 'AMOUNT_MISMATCH',
                        'severity': 'HIGH',
                        'details': f"Amount differs: {source1}=₹{amount1}, {source2}=₹{amount2}",
                        'sources': [source1, source2],
                        'values': {source1: amount1, source2: amount2}
                    })
                
                # Check status mismatch
                status1 = txn1.get('status', '').upper()
                status2 = txn2.get('status', '').upper()
                if status1 != status2:
                    mismatches.append({
                        'type': 'STATUS_MISMATCH',
                        'severity': 'MEDIUM',
                        'details': f"Status differs: {source1}={status1}, {source2}={status2}",
                        'sources': [source1, source2],
                        'values': {source1: status1, source2: status2}
                    })
                
                # Check currency mismatch
                currency1 = txn1.get('currency', 'INR')
                currency2 = txn2.get('currency', 'INR')
                if currency1 != currency2:
                    mismatches.append({
                        'type': 'CURRENCY_MISMATCH',
                        'severity': 'HIGH',
                        'details': f"Currency differs: {source1}={currency1}, {source2}={currency2}",
                        'sources': [source1, source2],
                        'values': {source1: currency1, source2: currency2}
                    })
                
                # Check account ID mismatch
                account1 = txn1.get('account_id')
                account2 = txn2.get('account_id')
                if account1 and account2 and account1 != account2:
                    mismatches.append({
                        'type': 'ACCOUNT_MISMATCH',
                        'severity': 'HIGH',
                        'details': f"Account ID differs: {source1}={account1}, {source2}={account2}",
                        'sources': [source1, source2],
                        'values': {source1: account1, source2: account2}
                    })
                
                # Check timestamp mismatch (if both have timestamps)
                if txn1.get('timestamp') and txn2.get('timestamp'):
                    try:
                        time1 = datetime.fromisoformat(txn1['timestamp'].replace('Z', '+00:00'))
                        time2 = datetime.fromisoformat(txn2['timestamp'].replace('Z', '+00:00'))
                        time_diff = abs((time1 - time2).total_seconds())
                        
                        if time_diff > self.time_tolerance:
                            mismatches.append({
                                'type': 'TIMESTAMP_MISMATCH',
                                'severity': 'LOW',
                                'details': f"Timestamp differs by {time_diff:.0f}s: {source1}={txn1['timestamp']}, {source2}={txn2['timestamp']}",
                                'sources': [source1, source2],
                                'values': {source1: txn1['timestamp'], source2: txn2['timestamp']}
                            })
                    except Exception as e:
                        logger.warning(f"Error parsing timestamps: {e}")
        
        # Check for missing fields
        all_fields = set()
        for txn in sources.values():
            all_fields.update(txn.keys())
        
        for field in ['amount', 'status', 'account_id']:
            if field in all_fields:
                missing_sources = []
                for source, txn in sources.items():
                    if field not in txn or txn[field] is None:
                        missing_sources.append(source)
                
                if missing_sources:
                    mismatches.append({
                        'type': 'MISSING_FIELD',
                        'severity': 'MEDIUM',
                        'details': f"Field '{field}' missing in sources: {', '.join(missing_sources)}",
                        'sources': missing_sources,
                        'field': field
                    })
        
        return mismatches
    
    def get_pending_count(self) -> int:
        """Get count of transactions pending reconciliation"""
        with self.lock:
            return len(self.pending_transactions)
    
    def get_reconciled_count(self) -> int:
        """Get count of reconciled transactions"""
        with self.lock:
            return len(self.reconciled_transactions)
    
    def get_mismatch_count(self) -> int:
        """Get count of detected mismatches"""
        with self.lock:
            return len(self.detected_mismatches)
    
    def get_recent_mismatches(self, limit: int = 20) -> List[dict]:
        """Get recent mismatches"""
        with self.lock:
            return self.detected_mismatches[-limit:]
    
    def get_recent_reconciled(self, limit: int = 50) -> List[dict]:
        """Get recent reconciled transactions"""
        with self.lock:
            return self.reconciled_transactions[-limit:]
    
    def get_statistics(self) -> dict:
        """Get reconciliation statistics"""
        with self.lock:
            total_reconciled = len(self.reconciled_transactions)
            total_mismatches = len([r for r in self.reconciled_transactions if r['status'] == 'MISMATCH'])
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

# Global reconciliation engine instance
reconciliation_engine = ReconciliationEngine()