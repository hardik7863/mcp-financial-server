"""In-memory sliding-window rate limiter for SSE transport."""

import time
from collections import defaultdict

from src.utils.errors import RateLimitExceededError


class RateLimiter:
    """Sliding window rate limiter keyed by client identifier."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check(self, client_id: str = "default") -> None:
        """Check rate limit. Raises RateLimitExceededError if exceeded."""
        now = time.monotonic()
        window_start = now - self.window_seconds

        # Prune old entries
        self._requests[client_id] = [
            t for t in self._requests[client_id] if t > window_start
        ]

        if len(self._requests[client_id]) >= self.max_requests:
            raise RateLimitExceededError()

        self._requests[client_id].append(now)

    def reset(self, client_id: str = "default") -> None:
        """Reset rate limit for a client."""
        self._requests.pop(client_id, None)


# Singleton instance — configured at startup from settings
_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    global _limiter
    if _limiter is None:
        from src.config.env import get_settings
        settings = get_settings()
        _limiter = RateLimiter(max_requests=settings.rate_limit_rpm)
    return _limiter
