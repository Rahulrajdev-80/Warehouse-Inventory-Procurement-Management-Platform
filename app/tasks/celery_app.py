from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery = Celery(
    "warehouse_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.inventory_tasks",
        "app.tasks.alert_tasks",
        "app.tasks.report_tasks",
    ]
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Configure Celery Beat Periodic Schedules
celery.conf.beat_schedule = {
    "reconcile-inventory-every-6-hours": {
        "task": "app.tasks.inventory_tasks.reconcile_inventory_task",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    "check-expired-and-low-stock-daily": {
        "task": "app.tasks.alert_tasks.check_expired_and_low_stock_task",
        "schedule": crontab(minute=0, hour=1), # Every day at 1 AM
    },
    "calculate-supplier-performance-weekly": {
        "task": "app.tasks.report_tasks.calculate_supplier_performance_task",
        "schedule": crontab(minute=0, hour=2, day_of_week=0), # Every Sunday at 2 AM
    },
    "daily-inventory-report": {
        "task": "app.tasks.report_tasks.generate_daily_inventory_report_task",
        "schedule": crontab(minute=0, hour=23), # Every day at 11 PM
    },
}
