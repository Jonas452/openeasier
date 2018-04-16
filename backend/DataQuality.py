import os
import django
import pandas as pd
from ckanapi import RemoteCKAN
from dateutil.parser import parse

os.environ["DJANGO_SETTINGS_MODULE"] = 'openeasier.settings'
django.setup()

from common.models import Resource, CKANInstance, DBColumn, DBTable


class DataQuality:

    def __init__(self, resource_id):
        self.resource = Resource.objects.get(id=resource_id)
        self.ckan_instance = CKANInstance.objects.get(id=self.resource.ckan.id)

        self.my_ckan = RemoteCKAN(self.ckan_instance.url)

        temp_resource = self.my_ckan.action.resource_show(id=self.resource.ckan_resource_id)
        url = (temp_resource.get("url")).replace("http://localhost/", self.ckan_instance.url)

        self.data = pd.read_csv(url, encoding="ISO-8859-1")

        self.data_len = len(self.data)
        self.remove_ids_and_fks()

    def remove_ids_and_fks(self):

        db_tables = DBTable.objects.filter(resource=self.resource) | DBTable.objects.filter(
            db_table__resource=self.resource)

        for column in self.data.columns:
            for db_table in db_tables:
                if column == db_table.primary_key or column == db_table.fk_name:
                    del self.data[column]
                    break;

    def columns_missing_data_(self):

        columns_assessment = []

        for column in self.data.columns:
            missing = 100 - ((self.data[column].count() / self.data_len) * 100)
            bg_color = 'bg-green'

            if missing >= 90:
                bg_color = 'bg-red'
            elif missing >= 60:
                bg_color = 'bg-yellow'

            temp_column = {
                'name': column,
                'missing': int(missing),
                'bg_color': bg_color,
            }

            columns_assessment.append(temp_column)

        return columns_assessment

    def columns_format_consistency(self):

        temp_format_consistency = []

        for column in self.data.columns:

            temp_data = self.data.dropna(subset=[column])

            numeric_count = 0
            date_count = 0
            text_count = 0
            total_count = len(temp_data)

            if total_count > 0:

                for data in temp_data[column]:
                    temp_type = type(data)

                    if (temp_type == float) or (temp_type == int):
                        numeric_count = numeric_count + 1
                    elif temp_type == str:
                        if data.isnumeric():
                            numeric_count = numeric_count + 1
                        elif self.isdate(data):
                            date_count = date_count + 1
                        else:
                            text_count = text_count + 1

                    '''
                    if data.isnumeric():
                        numeric_count = numeric_count + 1
                    elif self.isdate(data):
                        date_count = date_count + 1
                    else:
                        text_count + 1
                    '''

                perc_numeric = round(((numeric_count / total_count) * 100), 2)
                perc_date = round(((date_count / total_count) * 100), 2)
                perc_text = round(((text_count / total_count) * 100), 2)

                if perc_numeric == 100 or perc_date == 100 or perc_text == 100:
                    bg_color = 'bg-green'
                elif perc_numeric > 0 and perc_date > 0 and perc_text > 0:
                    bg_color = 'bg-red'
                else:
                    bg_color = 'bg-yellow'

                temp_column = {
                    'name': column,
                    'numeric_count': perc_numeric,
                    'date_count': perc_date,
                    'text_count': perc_text,
                    'bg_color': bg_color,
                }

                temp_format_consistency.append(temp_column)

            '''
            columns_grouped = data_column.groupby(column)

            for group in columns_grouped.groups:
                print(group)
                if group.isnumeric():
                    print('Number')
                elif self.isdate(group):
                    print('Date')
                else:
                    print('Text')
            '''

        return temp_format_consistency;

    def isdate(self, value):
        try:
            parse(value)
            return True
        except ValueError:
            return False
