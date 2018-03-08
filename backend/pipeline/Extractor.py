import os
import csv
import datetime
import django

os.environ["DJANGO_SETTINGS_MODULE"] = 'openeasier.settings'
django.setup()

from backend.database.TableExtractor import TableExtractor
from backend.database.MultiTableExtractor import MultiTableExtractor
from common.models import DBConfig, DBColumn, DBTable, PublicationLog
from backend.Log import Log


class Extractor:
    def __init__(self, resource, resource_schedule):
        self.table = resource.table
        self.db_config = DBConfig.objects.get(dbschema__dbtable=self.table)
        self.resource_schedule = resource_schedule

    def pre_run(self):
        # TODO CHECK DATABASE CONNECTION
        # TODO CHECK TABLE/SCHEMA EXISTS
        # TODO CHECK COLUMNS EXISTS
        pass

    def run(self):

        fk_tables = DBTable.objects.filter(db_table=self.table)

        Log.register('Preparing table(s) and column(s)', self.resource_schedule, PublicationLog.SUCCESS_TAG)
        if len(fk_tables) > 0:
            extractor = MultiTableExtractor(self.db_config, self.table, fk_tables)

            self.columns = extractor.get_columns()
            self.table_data = extractor.get_data()

        else:
            extractor = TableExtractor(self.db_config, self.table.name, self.table.db_schema.name)

            self.columns = Extractor.prepare_columns(self.table)
            self.table_data = extractor.get_data(self.columns)

        Log.register('Creating CSV file', self.resource_schedule, PublicationLog.SUCCESS_TAG)
        self.create_csv()

    def pos_run(self):
        pass

    @staticmethod
    def prepare_columns(p_table):
        columns = []
        for column in DBColumn.objects.filter(db_table=p_table):
            columns.append(column.name)

        if p_table.primary_key is not None:
            columns.append(p_table.primary_key)

        return columns

    def create_csv(self):
        today_date = datetime.datetime.today().strftime('%Y-%m-%d')

        parcial_path = 'working/' + self.table.name

        if not os.path.exists(parcial_path):
            os.makedirs(parcial_path)

        self.path = parcial_path + '/' + today_date + '_' + self.table.name + '.csv'

        with open(self.path, 'w', newline='') as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', fieldnames=self.columns)
            writer.writeheader()

            for row in self.table_data:
                writer.writerow(row)
