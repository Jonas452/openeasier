import os
import django
from ckanapi import RemoteCKAN

os.environ["DJANGO_SETTINGS_MODULE"] = 'openeasier.settings'
django.setup()
from common.models import CKANInstance, Resource, ResourceSchedule, UserCkanKey, PublicationLog
from .Loader import Loader
from .Extractor import Extractor
from .DataDictionary import DataDictionary
from backend.Log import Log


class Pipeline:
    def __init__(self, resource_schedule):

        self.resource_schedule = resource_schedule
        self.resource = Resource.objects.get(id=self.resource_schedule.resource.id)

        Log.register('Execution started', self.resource_schedule, PublicationLog.SUCCESS_TAG)

        self.ckan_instance = CKANInstance.objects.get(id=self.resource.ckan.id)
        self.user_api_key = UserCkanKey.objects.get(user=self.resource.user)

        self.my_ckan = RemoteCKAN(self.ckan_instance.url, self.user_api_key.ckan_key)

        self.extractor = Extractor(self.resource, resource_schedule)
        self.loader = Loader(self.resource, self.my_ckan, resource_schedule)
        self.data_dictionary = DataDictionary(self.resource, self.my_ckan, resource_schedule)

        self.final_status = ResourceSchedule.STATUS_FINISHED

    def execute(self):
        self.set_resource_schedule_running()

        try:
            self.pre_run()
            self.run()
            self.pos_run()
        except Exception as ex:
            template = "An exception of type {0} occurred. Message:\n{1}"
            message = template.format(type(ex).__name__, ex)

            Log.register(message, self.resource_schedule, PublicationLog.FAILED_TAG)
            self.final_status = ResourceSchedule.STATUS_FAILED

        self.set_resource_schedule_final_status()

        Log.register('Execution finished', self.resource_schedule, PublicationLog.SUCCESS_TAG)

    def pre_run(self):
        self.extractor.pre_run()
        # TODO Add transform.pre_run() method
        self.loader.pre_run()
        self.data_dictionary.pre_run()

    def run(self):

        Log.register('Extracting data started', self.resource_schedule, PublicationLog.SUCCESS_TAG)
        self.extractor.run()
        Log.register('Extracting data finished', self.resource_schedule, PublicationLog.SUCCESS_TAG)

        # TODO Add trasnform.run() method

        Log.register('Loading data started', self.resource_schedule, PublicationLog.SUCCESS_TAG)
        self.loader.run(self.extractor.path)
        Log.register('Loading data finished', self.resource_schedule, PublicationLog.SUCCESS_TAG)

        Log.register('Data Dictionary started', self.resource_schedule, PublicationLog.SUCCESS_TAG)
        self.data_dictionary.run()
        Log.register('Data Dictionary finished', self.resource_schedule, PublicationLog.SUCCESS_TAG)

    def pos_run(self):
        self.set_resource_id()
        self.extractor.pos_run()
        self.loader.pos_run()
        self.data_dictionary.pos_run()

    def set_resource_schedule_running(self):
        self.resource_schedule.execution_status = ResourceSchedule.STATUS_RUNNING
        self.resource_schedule.save()

    def set_resource_schedule_final_status(self):
        self.resource_schedule.execution_status = self.final_status
        self.resource_schedule.save()

    def set_resource_id(self):
        self.resource.ckan_resource_id = self.loader.resource_published.get('id')
        self.resource.save()
