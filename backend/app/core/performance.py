"""Small dependency-free performance primitives."""

from __future__ import annotations

from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import dataclass
from threading import Lock
from time import monotonic
from typing import Iterator


@dataclass(frozen=True)
class MetricSample:
    name: str
    duration_ms: float


class MetricsStore:
    def __init__(self, *, max_samples: int = 500) -> None:
        self._samples: OrderedDict[str, list[float]] = OrderedDict()
        self._max_samples = max_samples
        self._lock = Lock()

    def record(self, name: str, duration_ms: float) -> None:
        with self._lock:
            values = self._samples.setdefault(name, [])
            values.append(duration_ms)
            del values[:-self._max_samples]

    def snapshot(self) -> dict[str, dict[str, float | int]]:
        with self._lock:
            return {
                name: {
                    "count": len(values),
                    "last_ms": values[-1],
                    "average_ms": sum(values) / len(values),
                }
                for name, values in self._samples.items()
                if values
            }

    def clear(self) -> None:
        with self._lock:
            self._samples.clear()


@contextmanager
def measure(name: str, store: MetricsStore) -> Iterator[None]:
    started = monotonic()
    try:
        yield
    finally:
        store.record(name, (monotonic() - started) * 1000)


class BoundedTTLCache:
    """Thread-safe bounded cache for immutable deterministic results."""

    def __init__(self, *, max_size: int = 128, ttl_seconds: float = 300) -> None:
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._values: OrderedDict[str, tuple[float, object]] = OrderedDict()
        self._lock = Lock()

    def get(self, key: str) -> object | None:
        now = monotonic()
        with self._lock:
            entry = self._values.pop(key, None)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at <= now:
                return None
            self._values[key] = (expires_at, value)
            return value

    def set(self, key: str, value: object) -> None:
        with self._lock:
            self._values.pop(key, None)
            self._values[key] = (monotonic() + self.ttl_seconds, value)
            while len(self._values) > self.max_size:
                self._values.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._values.clear()


metrics_store = MetricsStore()
