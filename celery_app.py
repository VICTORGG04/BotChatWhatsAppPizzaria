from celery import Celery
from celery.signals import worker_ready, worker_shutdown
import logging

from config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "pizzaria_bot",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    result_expires=3600,
    task_routes={
        "tasks.registrar_pedido_google_sheets": {"queue": "sheets"},
        "tasks.registrar_pedido_excel": {"queue": "excel"},
        "tasks.registrar_pedido_sqlite": {"queue": "database"},
    },
    beat_schedule={
        "limpar-sessoes-expiradas": {
            "task": "tasks.limpar_sessoes_expiradas",
            "schedule": 300.0,  # 5 minutos
        },
    },
)


@worker_ready.connect
def worker_ready_handler(**kwargs):
    logger.info("Worker Celery iniciado")


@worker_shutdown.connect
def worker_shutdown_handler(**kwargs):
    logger.info("Worker Celery finalizando")


if __name__ == "__main__":
    celery_app.start()