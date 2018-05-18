import os
import django
import datetime
import time

os.environ["DJANGO_SETTINGS_MODULE"] = 'openeasier.settings'
django.setup()

from common.models import ResourceSchedule
from backend.pipeline.Pipeline import Pipeline
from backend.Scheduler import Scheduler


class Publisher:
    def __init__(self):

        while True:

            now = datetime.datetime.now()
            now = now.strftime("%Y-%m-%d")

            resources = ResourceSchedule.objects.filter(schedule_date_time=now)
            resources = resources.filter(execution_status=ResourceSchedule.STATUS_SCHEDULED)

            for resource_schedule in resources:

                pipeline = Pipeline(resource_schedule)
                pipeline.execute()

            Scheduler.schedule_all_resources()

            time.sleep(30)


Publisher()
