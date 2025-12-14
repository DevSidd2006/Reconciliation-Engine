from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.transaction import Transaction
from models.mismatch import Mismatch

TIME_THRESHOLD_MINUTES = 5      # timestamp mismatch threshold
DUPLICATE_WINDOW_SECONDS = 60   # duplicate txn window

class ReconciliationEngine:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # 1) Load all transactions for a given txn_id
    # ---------------------------------------------------------
    def load_transactions(self, txn_id: str):
        return (
            self.db.query(Transaction)
            .filter(Transaction.txn_id == txn_id)
            .all()
        )

    # ---------------------------------------------------------
    # 2) Main entrypoint — detect mismatches
    # ---------------------------------------------------------
    def detect_mismatches(self, txn_id: str):
        txns = self.load_transactions(txn_id)

        if not txns:
            return []

        sources = {t.source: t for t in txns}
        mismatches = []

        # ---------------------------------------------------------
        # 3) Missing records
        # ---------------------------------------------------------
        expected = {"core", "gateway", "mobile"}
        missing = expected - set(sources.keys())

        for src in missing:
            mismatches.append({
                "tx_id": txn_id,
                "type": f"MISSING_IN_{src.upper()}",
                "details": f"{src} did not report this transaction"
            })

        # ---------------------------------------------------------
        # 4) Amount mismatch
        # ---------------------------------------------------------
        amounts = {src: t.amount for src, t in sources.items()}
        if len(set(amounts.values())) > 1:
            mismatches.append({
                "tx_id": txn_id,
                "type": "AMOUNT_MISMATCH",
                "details": str(amounts)
            })

        # ---------------------------------------------------------
        # 5) Status mismatch
        # ---------------------------------------------------------
        statuses = {src: t.status for src, t in sources.items() if t.status}
        if len(set(statuses.values())) > 1:
            mismatches.append({
                "tx_id": txn_id,
                "type": "STATUS_MISMATCH",
                "details": str(statuses)
            })

        # ---------------------------------------------------------
        # 6) Timestamp mismatch
        # ---------------------------------------------------------
        times = [t.timestamp for t in txns if t.timestamp]
        if len(times) > 1:
            if (max(times) - min(times)) > timedelta(minutes=TIME_THRESHOLD_MINUTES):
                mismatches.append({
                    "tx_id": txn_id,
                    "type": "TIME_MISMATCH",
                    "details": f"Difference = {max(times) - min(times)}"
                })

        # ---------------------------------------------------------
        # 7) Currency mismatch
        # ---------------------------------------------------------
        currencies = {src: t.currency for src, t in sources.items()}
        if len(set(currencies.values())) > 1:
            mismatches.append({
                "tx_id": txn_id,
                "type": "CURRENCY_MISMATCH",
                "details": str(currencies)
            })

        # ---------------------------------------------------------
        # 8) Duplicate transactions (same source repeated)
        # ---------------------------------------------------------
        duplicates = {}
        for t in txns:
            duplicates.setdefault(t.source, []).append(t)

        for src, entries in duplicates.items():
            if len(entries) > 1:
                mismatches.append({
                    "tx_id": txn_id,
                    "type": "DUPLICATE_TRANSACTION",
                    "details": f"{src} sent {len(entries)} copies"
                })

        # ---------------------------------------------------------
        # 9) MULTIPLE mismatches
        # ---------------------------------------------------------
        if len(mismatches) > 1:
            mismatches.append({
                "tx_id": txn_id,
                "type": "MULTIPLE_MISMATCH",
                "details": f"{len(mismatches)} mismatches found"
            })

        # ---------------------------------------------------------
        # Save to DB
        # ---------------------------------------------------------
        for m in mismatches:
            record = Mismatch(
                id=f"{m['tx_id']}_{m['type']}_{datetime.utcnow().timestamp()}",
                txn_id=m["tx_id"],
                mismatch_type=m["type"],
                details=m["details"],
                detected_at=datetime.utcnow()
            )
            self.db.add(record)

        self.db.commit()
        return mismatches