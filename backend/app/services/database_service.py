"""
Database service for transaction reconciliation
Handles all database operations for transactions and mismatches
Enhanced with Redis caching for banking-grade performance
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from collections import defaultdict

from ..db.database import SessionLocal
from ..models.transaction import Transaction
from ..models.mismatch import Mismatch
from .redis_service import redis_service

class DatabaseService:
    def __init__(self):
        pass
    
    def get_db(self):
        """Get database session"""
        db = SessionLocal()
        try:
            return db
        except Exception:
            db.close()
            raise
    
    # ==================== TRANSACTION OPERATIONS ====================
    
    def save_transaction(self, transaction_data: dict) -> bool:
        """Save a transaction to database"""
        db = self.get_db()
        try:
            # Use current time for all transactions to ensure correct timestamps
            timestamp = datetime.now()
            
            # Get current time for all timestamp fields
            current_time = datetime.now()
            
            transaction = Transaction(
                txn_id=transaction_data['txn_id'],
                amount=float(transaction_data.get('amount', 0)),
                status=transaction_data.get('status', 'UNKNOWN'),
                timestamp=current_time,
                currency=transaction_data.get('currency', 'INR'),
                account_id=transaction_data.get('account_id'),
                source=transaction_data['source'],
                reconciliation_status='PENDING',
                created_at=current_time,
                updated_at=current_time
            )
            
            db.add(transaction)
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error saving transaction: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def update_reconciliation_status(self, txn_id: str, status: str, sources: List[str]) -> bool:
        """Update reconciliation status for all transactions with given txn_id"""
        db = self.get_db()
        try:
            transactions = db.query(Transaction).filter(Transaction.txn_id == txn_id).all()
            
            for txn in transactions:
                txn.reconciliation_status = status
                txn.reconciled_at = datetime.now()
                txn.reconciled_with_sources = json.dumps(sources)
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error updating reconciliation status: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_transactions(self, limit: int = 50, source: Optional[str] = None, 
                        status: Optional[str] = None) -> List[Dict]:
        """Get transactions with optional filtering - Redis cached for performance"""
        # Create cache key from parameters
        cache_params = {'limit': limit, 'source': source, 'status': status}
        
        # Try Redis cache first
        if redis_service.is_connected():
            cached_result = redis_service.get_cached_response('get_transactions', cache_params)
            if cached_result:
                return cached_result
        
        db = self.get_db()
        try:
            query = db.query(Transaction).order_by(desc(Transaction.created_at))
            
            if source:
                query = query.filter(Transaction.source == source)
            if status:
                query = query.filter(Transaction.status == status)
            
            transactions = query.limit(limit).all()
            
            result = [
                {
                    'id': txn.id,
                    'txn_id': txn.txn_id,
                    'amount': txn.amount,
                    'status': txn.status,
                    'timestamp': txn.timestamp.isoformat() if txn.timestamp else None,
                    'currency': txn.currency,
                    'account_id': txn.account_id,
                    'source': txn.source,
                    'reconciliation_status': txn.reconciliation_status,
                    'reconciled_at': txn.reconciled_at.isoformat() if txn.reconciled_at else None,
                    'reconciled_with_sources': json.loads(txn.reconciled_with_sources) if txn.reconciled_with_sources else [],
                    'created_at': txn.created_at.isoformat()
                }
                for txn in transactions
            ]
            
            # Cache the result
            if redis_service.is_connected():
                redis_service.cache_api_response('get_transactions', cache_params, result)
            
            return result
            
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
        finally:
            db.close()
    
    def get_transactions_by_txn_id(self, txn_id: str) -> List[Dict]:
        """Get all transactions for a specific transaction ID"""
        db = self.get_db()
        try:
            transactions = db.query(Transaction).filter(Transaction.txn_id == txn_id).all()
            
            return [
                {
                    'id': txn.id,
                    'txn_id': txn.txn_id,
                    'amount': txn.amount,
                    'status': txn.status,
                    'timestamp': txn.timestamp.isoformat() if txn.timestamp else None,
                    'currency': txn.currency,
                    'account_id': txn.account_id,
                    'source': txn.source,
                    'reconciliation_status': txn.reconciliation_status,
                    'created_at': txn.created_at.isoformat()
                }
                for txn in transactions
            ]
            
        except Exception as e:
            print(f"Error getting transactions by txn_id: {e}")
            return []
        finally:
            db.close()
    
    # ==================== MISMATCH OPERATIONS ====================
    
    def save_mismatch(self, mismatch_data: dict) -> bool:
        """Save a mismatch to database"""
        db = self.get_db()
        try:
            # Get current time for all timestamp fields
            current_time = datetime.now()
            
            mismatch = Mismatch(
                txn_id=mismatch_data['txn_id'],
                mismatch_type=mismatch_data['type'],
                severity=mismatch_data['severity'],
                details=mismatch_data['details'],
                sources_involved=json.dumps(mismatch_data.get('sources_involved', [])),
                expected_value=mismatch_data.get('expected_value'),
                actual_value=mismatch_data.get('actual_value'),
                difference_amount=mismatch_data.get('difference_amount'),
                status='OPEN',
                detected_at=current_time,
                created_at=current_time,
                updated_at=current_time
            )
            
            db.add(mismatch)
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error saving mismatch: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_mismatches(self, limit: int = 50, severity: Optional[str] = None,
                      mismatch_type: Optional[str] = None, status: Optional[str] = None, 
                      txn_id: Optional[str] = None) -> List[Dict]:
        """Get mismatches with optional filtering"""
        db = self.get_db()
        try:
            query = db.query(Mismatch).order_by(desc(Mismatch.detected_at))
            
            if severity:
                query = query.filter(Mismatch.severity == severity)
            if mismatch_type:
                query = query.filter(Mismatch.mismatch_type == mismatch_type)
            if status:
                query = query.filter(Mismatch.status == status)
            if txn_id:
                query = query.filter(Mismatch.txn_id == txn_id)
            
            mismatches = query.limit(limit).all()
            
            return [
                {
                    'id': m.id,
                    'txn_id': m.txn_id,
                    'type': m.mismatch_type,
                    'severity': m.severity,
                    'details': m.details,
                    'sources_involved': json.loads(m.sources_involved) if m.sources_involved else [],
                    'expected_value': m.expected_value,
                    'actual_value': m.actual_value,
                    'difference_amount': m.difference_amount,
                    'status': m.status,
                    'detected_at': m.detected_at.isoformat(),
                    'resolved_at': m.resolved_at.isoformat() if m.resolved_at else None,
                    'resolution_notes': m.resolution_notes
                }
                for m in mismatches
            ]
            
        except Exception as e:
            print(f"Error getting mismatches: {e}")
            return []
        finally:
            db.close()
    
    # ==================== STATISTICS OPERATIONS ====================
    
    def get_transaction_stats(self) -> Dict:
        """Get comprehensive transaction statistics - Redis cached for performance"""
        # Try Redis cache first
        if redis_service.is_connected():
            cached_stats = redis_service.get_cached_stats('transaction_stats')
            if cached_stats:
                return cached_stats
        
        db = self.get_db()
        try:
            # Total counts
            total_transactions = db.query(Transaction).count()
            total_mismatches = db.query(Mismatch).count()
            
            # Reconciliation status counts
            reconciliation_stats = db.query(
                Transaction.reconciliation_status,
                func.count(Transaction.id)
            ).group_by(Transaction.reconciliation_status).all()
            
            reconciliation_counts = {status: count for status, count in reconciliation_stats}
            
            # Source distribution
            source_stats = db.query(
                Transaction.source,
                func.count(Transaction.id)
            ).group_by(Transaction.source).all()
            
            source_counts = {source: count for source, count in source_stats}
            
            # Status distribution
            status_stats = db.query(
                Transaction.status,
                func.count(Transaction.id)
            ).group_by(Transaction.status).all()
            
            status_counts = {status: count for status, count in status_stats}
            
            # Mismatch type distribution
            mismatch_type_stats = db.query(
                Mismatch.mismatch_type,
                func.count(Mismatch.id)
            ).group_by(Mismatch.mismatch_type).all()
            
            mismatch_type_counts = {mtype: count for mtype, count in mismatch_type_stats}
            
            # Success rate calculation
            matched_count = reconciliation_counts.get('MATCHED', 0)
            mismatched_count = reconciliation_counts.get('MISMATCH', 0)
            total_reconciled = matched_count + mismatched_count
            success_rate = (matched_count / total_reconciled * 100) if total_reconciled > 0 else 100
            
            # Recent activity (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            recent_transactions = db.query(Transaction).filter(
                Transaction.created_at >= yesterday
            ).count()
            
            recent_mismatches = db.query(Mismatch).filter(
                Mismatch.detected_at >= yesterday
            ).count()
            
            stats = {
                'total_transactions': total_transactions,
                'total_mismatches': total_mismatches,
                'total_reconciled': total_reconciled,
                'success_rate': round(success_rate, 1),
                'pending_reconciliation': reconciliation_counts.get('PENDING', 0),
                'reconciliation_breakdown': reconciliation_counts,
                'source_distribution': source_counts,
                'status_distribution': status_counts,
                'mismatch_types': mismatch_type_counts,
                'recent_activity': {
                    'transactions_24h': recent_transactions,
                    'mismatches_24h': recent_mismatches
                }
            }
            
            # Cache the stats
            if redis_service.is_connected():
                redis_service.cache_stats('transaction_stats', stats)
            
            return stats
            
        except Exception as e:
            print(f"Error getting transaction stats: {e}")
            return {
                'total_transactions': 0,
                'total_mismatches': 0,
                'total_reconciled': 0,
                'success_rate': 100,
                'pending_reconciliation': 0,
                'reconciliation_breakdown': {},
                'source_distribution': {},
                'status_distribution': {},
                'mismatch_types': {},
                'recent_activity': {'transactions_24h': 0, 'mismatches_24h': 0}
            }
        finally:
            db.close()
    
    def get_health_status(self) -> Dict:
        """Get system health status"""
        db = self.get_db()
        try:
            # Check database connectivity
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            
            # Get recent activity
            last_hour = datetime.now() - timedelta(hours=1)
            recent_transactions = db.query(Transaction).filter(
                Transaction.created_at >= last_hour
            ).count()
            
            # Get last transaction
            last_transaction = None
            total_transactions = db.query(Transaction).count()
            if total_transactions > 0:
                last_txn = db.query(Transaction).order_by(
                    desc(Transaction.created_at)
                ).first()
                if last_txn:
                    last_transaction = last_txn.created_at.isoformat()
            
            # Determine system status
            if recent_transactions > 0:
                system_status = "HEALTHY"
            elif total_transactions > 0:
                system_status = "IDLE"
            else:
                system_status = "WAITING"
            
            return {
                'status': system_status,
                'database_connected': True,
                'last_transaction': last_transaction,
                'transactions_last_hour': recent_transactions,
                'total_transactions': total_transactions,
                'uptime': 'OK'
            }
            
        except Exception as e:
            print(f"Error getting health status: {e}")
            return {
                'status': 'ERROR',
                'database_connected': False,
                'error': str(e),
                'uptime': 'ERROR'
            }
        finally:
            db.close()

    def get_transactions_by_date(self, date) -> List[Dict]:
        """Get transactions for a specific date"""
        db = self.get_db()
        try:
            from datetime import datetime
            start_date = datetime.combine(date, datetime.min.time())
            end_date = datetime.combine(date, datetime.max.time())
            
            transactions = db.query(Transaction).filter(
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            ).all()
            
            return [
                {
                    'id': txn.id,
                    'txn_id': txn.txn_id,
                    'amount': txn.amount,
                    'status': txn.status,
                    'source': txn.source,
                    'created_at': txn.created_at.isoformat()
                }
                for txn in transactions
            ]
            
        except Exception as e:
            print(f"Error getting transactions by date: {e}")
            return []
        finally:
            db.close()
    
    def get_mismatches_by_date(self, date) -> List[Dict]:
        """Get mismatches for a specific date"""
        db = self.get_db()
        try:
            from datetime import datetime
            start_date = datetime.combine(date, datetime.min.time())
            end_date = datetime.combine(date, datetime.max.time())
            
            mismatches = db.query(Mismatch).filter(
                Mismatch.detected_at >= start_date,
                Mismatch.detected_at <= end_date
            ).all()
            
            return [
                {
                    'id': m.id,
                    'txn_id': m.txn_id,
                    'type': m.mismatch_type,
                    'severity': m.severity,
                    'detected_at': m.detected_at.isoformat()
                }
                for m in mismatches
            ]
            
        except Exception as e:
            print(f"Error getting mismatches by date: {e}")
            return []
        finally:
            db.close()
    
    def get_delayed_transactions_count(self, minutes: int = 5) -> int:
        """Get count of transactions with delays > specified minutes"""
        db = self.get_db()
        try:
            # Count transactions where reconciliation took longer than expected
            delayed = db.query(Transaction).filter(
                Transaction.reconciled_at.isnot(None),
                func.extract('epoch', Transaction.reconciled_at - Transaction.created_at) > minutes * 60
            ).count()
            
            return delayed
            
        except Exception as e:
            print(f"Error getting delayed transactions: {e}")
            return 0
        finally:
            db.close()
    
    def get_duplicate_transactions_count(self) -> int:
        """Get count of duplicate transactions"""
        db = self.get_db()
        try:
            # Find transactions with same txn_id and source (duplicates)
            duplicates = db.query(Transaction.txn_id, Transaction.source, func.count(Transaction.id)).group_by(
                Transaction.txn_id, Transaction.source
            ).having(func.count(Transaction.id) > 1).count()
            
            return duplicates
            
        except Exception as e:
            print(f"Error getting duplicate transactions: {e}")
            return 0
        finally:
            db.close()
    
    def get_timeline_stats(self, hours: int = 24, interval: str = "hour") -> List[Dict]:
        """Get timeline statistics for charts"""
        db = self.get_db()
        try:
            from datetime import datetime, timedelta
            
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Group by hour for simplicity
            if interval == "hour":
                timeline_data = []
                current_time = start_time
                
                while current_time < end_time:
                    next_time = current_time + timedelta(hours=1)
                    
                    # Count transactions in this hour
                    txn_count = db.query(Transaction).filter(
                        Transaction.created_at >= current_time,
                        Transaction.created_at < next_time
                    ).count()
                    
                    # Count mismatches in this hour
                    mismatch_count = db.query(Mismatch).filter(
                        Mismatch.detected_at >= current_time,
                        Mismatch.detected_at < next_time
                    ).count()
                    
                    timeline_data.append({
                        'hour': current_time.strftime('%H:00'),
                        'timestamp': current_time.isoformat(),
                        'transactions': txn_count,
                        'mismatches': mismatch_count
                    })
                    
                    current_time = next_time
                
                return timeline_data
            
            return []
            
        except Exception as e:
            print(f"Error getting timeline stats: {e}")
            return []
        finally:
            db.close()
    
    def get_recent_activity_stats(self, minutes: int = 30) -> Dict:
        """Get recent activity statistics for anomaly detection"""
        db = self.get_db()
        try:
            from datetime import datetime, timedelta
            
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            # Count recent transactions
            recent_transactions = db.query(Transaction).filter(
                Transaction.created_at >= cutoff_time
            ).count()
            
            # Count recent mismatches
            recent_mismatches = db.query(Mismatch).filter(
                Mismatch.detected_at >= cutoff_time
            ).count()
            
            # Calculate rates per minute
            transaction_rate = round(recent_transactions / minutes, 1)
            mismatch_rate = round(recent_mismatches / minutes, 1)
            
            return {
                'transaction_rate': transaction_rate,
                'mismatch_rate': mismatch_rate,
                'total_transactions': recent_transactions,
                'total_mismatches': recent_mismatches,
                'period_minutes': minutes
            }
            
        except Exception as e:
            print(f"Error getting recent activity stats: {e}")
            return {'transaction_rate': 0, 'mismatch_rate': 0, 'total_transactions': 0, 'total_mismatches': 0}
        finally:
            db.close()
    
    def get_source_delay_analysis(self) -> Dict[str, float]:
        """Analyze delays by source"""
        db = self.get_db()
        try:
            # Simplified delay analysis
            sources = ['core', 'gateway', 'mobile']
            delays = {}
            
            for source in sources:
                # Calculate average processing time for this source
                avg_delay = db.query(
                    func.avg(func.extract('epoch', Transaction.reconciled_at - Transaction.created_at))
                ).filter(
                    Transaction.source == source,
                    Transaction.reconciled_at.isnot(None)
                ).scalar()
                
                delays[source] = float(avg_delay) if avg_delay else 0.0
            
            return delays
            
        except Exception as e:
            print(f"Error getting source delay analysis: {e}")
            return {'core': 0.0, 'gateway': 0.0, 'mobile': 0.0}
        finally:
            db.close()

# Global database service instance
db_service = DatabaseService()