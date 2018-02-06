import os

import django
from ckanapi import NotFound

os.environ["DJANGO_SETTINGS_MODULE"] = 'openeasier.settings'
django.setup()

from common.models import CKANInstance
from backend.pipeline.exceptions.LoaderException import DatasetNotFound, ResourceNotFound


class Loader:
    def __init__(self, resource, my_ckan):
        self.resource = resource
        self.ckan_instance = CKANInstance.objects.get(id=self.resource.ckan.id)
        self.my_ckan = my_ckan

    def pre_run(self):
        # TODO CKAN EXISTS

        if not self.check_package_exists(self.resource.ckan_data_set_id):
            raise DatasetNotFound(
                "Dataset {%s} not found in {%s}." % (self.resource.ckan_data_set_id, self.ckan_instance.name))

        if self.resource.ckan_resource_id:
            if not self.check_resource_exists(self.resource.ckan_resource_id):
                raise ResourceNotFound(
                    "Resource {%s} not found in {%s}." % (self.resource.ckan_resource_id, self.ckan_instance.name))

        # TODO USER OK TO CREATE/UPDATE RESOURCE

    def run(self, csv_path):
        if self.resource.ckan_resource_id:
            self.resource_published = self.my_ckan.action.resource_update(
                id=self.resource.ckan_resource_id,
                name=self.resource.name,
                description=self.resource.description,
                primary_key=self.resource.table.primary_key,
                upload=open(csv_path, 'rb')
            )
        else:
            self.resource_published = self.my_ckan.action.resource_create(
                package_id=self.resource.ckan_data_set_id,
                name=self.resource.name,
                description=self.resource.description,
                primary_key=self.resource.table.primary_key,
                upload=open(csv_path, 'rb')
            )

    def pos_run(self):
        pass

    def check_package_exists(self, id):
        try:
            self.my_ckan.action.package_show(id=id)
            return True
        except NotFound:
            return False

    def check_resource_exists(self, id):
        try:
            self.my_ckan.action.resource_show(id=id)
            return True
        except NotFound:
            return False
