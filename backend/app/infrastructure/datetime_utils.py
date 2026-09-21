from datetime import datetime, timezone


def utc_now_naive() -> datetime:
    """Return current UTC time as a naive datetime.

    Database timestamps use PostgreSQL TIMESTAMP WITHOUT TIME ZONE.
    This helper preserves UTC semantics while returning a naive datetime.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
