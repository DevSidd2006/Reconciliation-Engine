import logging
from sqlalchemy.orm import Session
from datetime import datetime
from db.database import SessionLocal
from models.transaction import Transaction
from models.mismatch import Mismatch
from utils.socket_manager import socket_manager

logger = logging.getLogger(__name__)

class ReconciliationService:
    def __init__(self):
        pass

    async def process_transaction(self, data: dict):
        """
        Process a single transaction record:
        1. Save to DB.
        2. Check for mismatches.
        3. Emit events.
        """
        db = SessionLocal()
        try:
            # 1. Parse and Save
            txn = self._save_transaction(db, data)
            
            # 2. Reconcile
            await self._reconcile(db, txn)
            
            # 3. Emit Real-time Update
            await socket_manager.emit_transaction(data)
            
        except Exception as e:
            logger.error(f"Error processing transaction {data.get('txn_id')}: {e}")
            db.rollback()
        finally:
            db.close()

    def _save_transaction(self, db: Session, data: dict) -> Transaction:
        """Upsert transaction record"""
        # Convert timestamp str to datetime if needed
        ts = data.get('timestamp')
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                ts = datetime.utcnow()

        # Check if exists (idempotency)
        existing = db.query(Transaction).filter(
            Transaction.txn_id == data['txn_id'],
            Transaction.source == data['source']
        ).first()

        if existing:
            # Update fields
            existing.status = data['status']
            existing.amount = data['amount']
            existing.timestamp = ts
            txn = existing
        else:
            txn = Transaction(
                txn_id=data['txn_id'],
                amount=data['amount'],
                status=data['status'],
                timestamp=ts,
                currency=data.get('currency', 'USD'),
                account_id=data.get('account_id'),
                source=data['source']
            )
            db.add(txn)
        
        db.commit()
        db.refresh(txn)
        return txn

    async def _reconcile(self, db: Session, txn: Transaction):
        """
        Compare this transaction against other sources.
        Logic:
        - If 'core' says $100 and 'gateway' says $90 -> Mismatch
        - If 'core' says SUCCESS and 'mobile' says FAILED -> Mismatch
        """
        # Find related transactions (Same ID, different source)
        siblings = db.query(Transaction).filter(
            Transaction.txn_id == txn.txn_id,
            Transaction.source != txn.source
        ).all()

        if not siblings:
            return  # No comparison data yet

        for sibling in siblings:
            mismatch_found = False
            details = []

            # Check 1: Amount
            if abs(sibling.amount - txn.amount) > 0.01:
                mismatch_found = True
                details.append(f"Amount mismatch: {txn.source}({txn.amount}) vs {sibling.source}({sibling.amount})")

            # Check 2: Status (Simple rule: Both must be same final state)
            # Ignoring PENDING for now as it might be transient
            if txn.status != sibling.status and "PENDING" not in [txn.status, sibling.status]:
                mismatch_found = True
                details.append(f"Status mismatch: {txn.source}({txn.status}) vs {sibling.source}({sibling.status})")

            if mismatch_found:
                self._create_mismatch(db, txn.txn_id, txn.timestamp, "; ".join(details))

    def _create_mismatch(self, db: Session, txn_id: str, detected_at: datetime, details: str):
        """Create mismatch record and emit event"""
        # Idempotency check for mismatch
        existing = db.query(Mismatch).filter(
            Mismatch.txn_id == txn_id,
            Mismatch.details == details
        ).first()

        if not existing:
            mismatch_id = f"MIS-{txn_id}-{int(datetime.utcnow().timestamp())}"
            mismatch = Mismatch(
                id=mismatch_id,
                txn_id=txn_id,
                mismatch_type="DATA_INCONSISTENCY",
                detected_at=detected_at or datetime.utcnow(),
                details=details
            )
            db.add(mismatch)
            db.commit()
            
            # Async emit
            import asyncio
            # We can't await directly in sync db function, but _reconcile calls this and is async
            # However this helper is sync. Better to return the obj and emit in _reconcile
            # For simplicity, we'll assign it to a variable or use create_task if loop available
            # But process_transaction is async, so we can just emit there if we refactor.
            # Actually, let's just emit here using the manager helper which is async
            # But we are in a sync function. Let's just create a task on the running loop.
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(socket_manager.emit_mismatch({
                        "id": mismatch.id,
                        "txn_id": txn_id,
                        "type": "DATA_INCONSISTENCY",
                        "details": details,
                        "detected_at": mismatch.detected_at.isoformat()
                    }))
            except RuntimeError:
                pass # No loop running

reconciliation_service = ReconciliationService()
