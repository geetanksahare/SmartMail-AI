from celery import Celery

from app.core.config import settings


def _build_redis_url(url: str) -> str:
    """
    Add the TLS requirement needed by Celery when using
    an Upstash Redis rediss:// connection.
    """
    if not url.startswith("rediss://"):
        return url

    if "ssl_cert_reqs=" in url:
        return url

    separator = "&" if "?" in url else "?"

    return (
        f"{url}"
        f"{separator}"
        f"ssl_cert_reqs=required"
    )


redis_url = _build_redis_url(
    settings.REDIS_URL
)


celery_app = Celery(
    "smartmail_ai",
    broker=redis_url,
    backend=redis_url,
    include=[
        "app.tasks.email_tasks",
    ],
)


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    timezone="UTC",
    enable_utc=True,

    task_track_started=True,

    task_acks_late=True,
    task_reject_on_worker_lost=True,

    worker_prefetch_multiplier=1,

    broker_connection_retry_on_startup=True,

    result_expires=3600,

    task_time_limit=300,
    task_soft_time_limit=270,
)