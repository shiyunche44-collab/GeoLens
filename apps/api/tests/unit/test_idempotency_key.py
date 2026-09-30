import uuid

from geolens.modules.collection.service import idempotency_key

P, Q = uuid.uuid4(), uuid.uuid4()


def test_key_is_stable_and_sensitive_to_every_dimension() -> None:
    base = idempotency_key(P, Q, "deepseek", "zh-CN", 0, "2026-09-30")
    assert base == idempotency_key(P, Q, "deepseek", "zh-CN", 0, "2026-09-30")
    variants = [
        idempotency_key(P, Q, "kimi", "zh-CN", 0, "2026-09-30"),
        idempotency_key(P, Q, "deepseek", "en-US", 0, "2026-09-30"),
        idempotency_key(P, Q, "deepseek", "zh-CN", 1, "2026-09-30"),
        idempotency_key(P, Q, "deepseek", "zh-CN", 0, "2026-10-01"),
        idempotency_key(P, uuid.uuid4(), "deepseek", "zh-CN", 0, "2026-09-30"),
    ]
    assert base not in variants and len(set(variants)) == len(variants)
