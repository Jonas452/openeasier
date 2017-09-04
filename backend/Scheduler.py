import os
import django
from datetime import datetime as DateTime, timedelta as TimeDelta

os.environ["DJANGO_SETTINGS_MODULE"] = 'openeasier.settings'
django.setup()

from common.models import Resource, ResourceSchedule


class Scheduler:
    @staticmethod
    def schedule_all_resources():
        resources = Resource.objects.filter(resource_status='ACTIVE')

        for resource in resources:
            Scheduler.schedule_resource(resource)

    @staticmethod
    def schedule_resource(resource):

        try:
            latest_schedule = ResourceSchedule.objects.filter(resource=resource)
            latest_schedule = latest_schedule.latest('id')
        except ResourceSchedule.DoesNotExist:
            latest_schedule = None

        new_schedule = ResourceSchedule()

        new_schedule.resource = resource
        new_schedule.execution_status = ResourceSchedule.STATUS_SCHEDULED

        if latest_schedule:

            if latest_schedule.execution_status == ResourceSchedule.STATUS_FINISHED:
                if resource.schedule_type == Resource.TYPE_DAY:
                    date_time = latest_schedule.schedule_date_time + TimeDelta(days=1)
                elif resource.schedule_type == Resource.TYPE_WEEK:
                    date_time = latest_schedule.schedule_date_time + TimeDelta(weeks=1)
                elif resource.schedule_type == Resource.TYPE_MONTH:
                    date_time = latest_schedule.schedule_date_time + TimeDelta(weeks=4)
                elif resource.schedule_type == Resource.TYPE_YEAR:
                    date_time = latest_schedule.schedule_date_time + TimeDelta(weeks=48)

                new_schedule.schedule_date_time = date_time
                new_schedule.save()

        else:
            new_schedule.schedule_date_time = resource.schedule_date_time
            new_schedule.save()

        return new_schedule
