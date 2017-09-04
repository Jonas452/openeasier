import csv
import datetime
import os

import django
from ckanapi import RemoteCKAN

os.environ["DJANGO_SETTINGS_MODULE"] = 'openeasier.settings'
django.setup()
from common.models import Resource, ResourceSchedule, DBColumn, DBConfig, CKANInstance, \
    UserCkanKey
from backend.database.TableExtractor import TableExtractor
from backend.pipeline.Pipeline import Pipeline
from backend.Scheduler import Scheduler


class Publisher:
    def __init__(self):
        pipeline = Pipeline(ResourceSchedule.objects.get(id=142))
        pipeline.execute()

        #Scheduler.schedule_all_resources()

        '''
        today_date = datetime.datetime.today().strftime('%Y-%m-%d')

        resources_schedules_everyday = ResourceSchedule.objects.filter(resource__schedule_type=Resource.TYPE_DAY)

        ckan_instance = CKANInstance.objects.get(id=1)

        for resources_schedules in resources_schedules_everyday:
            resource = resources_schedules.resource
            user = resource.user
            user_api_key = UserCkanKey.objects.get(user=user)
            table = resource.table
            db_config = DBConfig.objects.get(dbschema__dbtable=table)

            my_ckan = RemoteCKAN(ckan_instance.url, apikey=user_api_key.ckan_key)

            extractor = TableExtractor(db_config, table.name, table.db_schema.name)

            columns = []
            for column in DBColumn.objects.filter(db_table=table):
                columns.append(column.name)

            columns.append(table.primary_key)

            table_data = extractor.get_data(columns)

            partical_path = 'working/' + table.name

            if not os.path.exists(partical_path):
                os.makedirs(partical_path)

            path = partical_path + '/' + today_date + '.csv'

            with open(path, 'w', newline='') as out_file:
                writer = csv.DictWriter(out_file, delimiter=',', fieldnames=columns)
                writer.writeheader()

                for row in table_data:
                    writer.writerow(row)

            my_ckan.action.resource_create(
                package_id=resource.ckan_data_set_id,
                name=resource.name,
                description=resource.description,
                primary_key='id',
                upload=open(path, 'rb'))
        '''

Publisher()
