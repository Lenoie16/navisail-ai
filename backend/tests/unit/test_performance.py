from time import sleep

from app.core.performance import BoundedTTLCache, MetricsStore, measure


def test_metrics_store_records_bounded_samples() -> None:
    store = MetricsStore(max_samples=2)
    with measure("compute", store):
        pass
    with measure("compute", store):
        pass
    with measure("compute", store):
        pass
    snapshot = store.snapshot()
    assert snapshot["compute"]["count"] == 2
    assert snapshot["compute"]["last_ms"] >= 0


def test_ttl_cache_expires_and_can_be_cleared() -> None:
    cache = BoundedTTLCache(max_size=1, ttl_seconds=0.01)
    cache.set("key", {"value": 1})
    assert cache.get("key") == {"value": 1}
    sleep(0.02)
    assert cache.get("key") is None
    cache.set("key", 2)
    cache.clear()
    assert cache.get("key") is None
