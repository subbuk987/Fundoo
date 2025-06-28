from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "fundoo",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
)

celery_app.conf.timezone = "Asia/Kolkata"

celery_app.conf.beat_schedule = {
    "send-daily-report": {
        "task": "fundoo.tasks.send_daily_report",
        "schedule": crontab(minute=0),
    },
}
