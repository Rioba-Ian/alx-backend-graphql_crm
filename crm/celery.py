import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")

app = Celery("crm")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.broker_url = "redis://localhost:6379/0"
app.conf.result_backend = "redis://localhost:6379/0"

app.conf.timezone = "UTC"

app.conf.beat_schedule = {
    "generate-crm-report": {
        "task": "crm.tasks.generate_crm_report",
        "schedule": 3600.0 * 24 * 7,  # every hour
    },
}
