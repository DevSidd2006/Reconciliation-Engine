import time
from collections import defaultdict, deque
from typing import Deque, Dict


class RateLimiter:
    """
    Simple in-memory sliding window rate limiter.
    Not suitable for multi-instance deployments; swap with Redis for production.
    """

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window
        dq = self.requests[key]

        # Drop outdated timestamps
        while dq and dq[0] < window_start:
            dq.popleft()

        if len(dq) >= self.limit:
            return False

        dq.append(now)
        return True


