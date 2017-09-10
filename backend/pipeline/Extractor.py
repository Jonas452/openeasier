import os
import csv
import datetime
import django

os.environ["DJANGO_SETTINGS_MODULE"] = 'openeasier.settings'
django.setup()

from backend.database.TableExtractor import TableExtractor
from common.models import DBConfig, DBColumn


class Extractor:
    def __init__(self, resource):
        self.table = resource.table
        self.db_config = DBConfig.objects.get(dbschema__dbtable=self.table)

    def pre_run(self):
        # TODO CHECK DATABASE CONNECTION
        # TODO CHECK TABLE/SCHEMA EXISTS
        # TODO CHECK COLUMNS EXISTS
        pass

    def run(self):
        extractor = TableExtractor(self.db_config, self.table.name, self.table.db_schema.name)

        self.columns = self.prepare_columns()
        self.table_data = extractor.get_data(self.columns)

        self.create_csv()

    def pos_run(self):
        pass

    def prepare_columns(self):
        columns = []
        for column in DBColumn.objects.filter(db_table=self.table):
            columns.append(column.name)

        columns.append(self.table.primary_key)

        return columns

    def create_csv(self):
        today_date = datetime.datetime.today().strftime('%Y-%m-%d')

        parcial_path = 'working/' + self.table.name

        if not os.path.exists(parcial_path):
            os.makedirs(parcial_path)

        self.path = parcial_path + '/' + today_date + '_extracted.csv'

        with open(self.path, 'w', newline='') as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', fieldnames=self.columns)
            writer.writeheader()

            for row in self.table_data:
                writer.writerow(row)
