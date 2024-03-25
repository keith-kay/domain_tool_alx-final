"""
WSGI config for domaintool project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
import threading
import schedule  # Add this line to import the schedule module
import time
from django.core.wsgi import get_wsgi_application
from domain_app.views import scheduled_update  # Replace 'your_app' with the actual name of your Django app

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "domaintool.settings")
application = get_wsgi_application()

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()