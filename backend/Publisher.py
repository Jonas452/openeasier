import os
import django
import datetime

os.environ["DJANGO_SETTINGS_MODULE"] = 'openeasier.settings'
django.setup()

from common.models import ResourceSchedule
from backend.pipeline.Pipeline import Pipeline
from backend.Scheduler import Scheduler


class Publisher:
    def __init__(self):

        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d")

        resource_schedules_today = ResourceSchedule.objects.filter(schedule_date_time=now)

        for resource_schedule in resource_schedules_today:
            pipeline = Pipeline(resource_schedule)
            pipeline.execute()

        Scheduler.schedule_all_resources()


Publisher()
