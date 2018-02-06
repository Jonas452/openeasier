import os
import django
from ckanapi import RemoteCKAN, NotFound

os.environ["DJANGO_SETTINGS_MODULE"] = 'openeasier.settings'
django.setup()
from common.models import CKANInstance, Resource, ResourceSchedule, UserCkanKey
from .Loader import Loader
from .Extractor import Extractor
from .DataDictionary import DataDictionary


class Pipeline:
    def __init__(self, resource_schedule):
        self.resource_schedule = resource_schedule
        self.resource = Resource.objects.get(id=self.resource_schedule.resource.id)

        self.ckan_instance = CKANInstance.objects.get(id=self.resource.ckan.id)
        self.user_api_key = UserCkanKey.objects.get(user=self.resource.user)

        self.my_ckan = RemoteCKAN(self.ckan_instance.url, self.user_api_key.ckan_key)

        self.extractor = Extractor(self.resource)
        self.loader = Loader(self.resource, self.my_ckan)
        self.data_dictionary = DataDictionary(self.resource, self.my_ckan)

        self.final_status = ResourceSchedule.STATUS_FINISHED

    def execute(self):
        self.set_resource_schedule_running()

        try:
            self.pre_run()
            self.run()
            self.pos_run()
        except Exception as ex:
            # TODO SAVE EXCEPTION NAME AND MSG IN LOG
            template = "An exception of type {0} occurred. Message:\n{1}"
            message = template.format(type(ex).__name__, ex)
            print(message)
            self.final_status = ResourceSchedule.STATUS_FAILED

        self.set_resource_schedule_final_status()

    def pre_run(self):
        self.extractor.pre_run()
        # TODO Add transform.pre_run() method
        self.loader.pre_run()
        self.data_dictionary.pre_run()

    def run(self):
        self.extractor.run()
        # TODO Add trasnform.run() method
        self.loader.run(self.extractor.path)
        self.data_dictionary.run()

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
