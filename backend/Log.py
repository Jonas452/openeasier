import os
import django

os.environ["DJANGO_SETTINGS_MODULE"] = 'openeasier.settings'
django.setup()

from common.models import PublicationLog


class Log:

    @staticmethod
    def register(message, resource_schedule, status):

        log = PublicationLog()
        log.log_message = message
        log.resource_schedule = resource_schedule
        log.log_status = status
        log.save()
