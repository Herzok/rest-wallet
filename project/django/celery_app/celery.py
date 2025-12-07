import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_wallet.settings")

app = Celery("rest_wallet")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()