from pygrametl.datasources import SQLSource
from .DatabaseConnection import DatabaseConnection
from common.models import DBColumn, DBTable


class MultiTableExtractor(DatabaseConnection):
    def __init__(self, db_config, main_table, fk_tables):
        super(MultiTableExtractor, self).__init__(db_config=db_config)

        self.main_table = main_table
        self.fk_tables = fk_tables

        self.prepare_columns_select()
        self.prepare_joins()

    def get_data(self):
        query = "SELECT " + self.columns + " FROM " + self.main_table.db_schema.name + '.' + self.main_table.name + self.joins

        data = list(SQLSource(connection=self.db_pgconn, query=query))

        sample_list = list()
        for sample_dict in data:
            sample_list.append(sample_dict)

        return sample_list

    def get_columns(self):

        columns = []
        columns.append(self.main_table.primary_key)

        # main table's columns
        for column in DBColumn.objects.filter(db_table=self.main_table):
            columns.append(column.name)

        # fk tables's columns
        for fk_table in self.fk_tables:
            for column in DBColumn.objects.filter(db_table=fk_table):
                columns.append(fk_table.name + '_' + column.name)

        return columns

    def prepare_columns_select(self):

        self.columns = self.main_table.db_schema.name + '.' + self.main_table.name + '.' + self.main_table.primary_key + ', '

        # main table's columns
        for column in DBColumn.objects.filter(db_table=self.main_table):
            self.columns += self.main_table.db_schema.name + '.' + self.main_table.name + '.' + column.name + ', '

        # fk tables's columns
        for fk_table in self.fk_tables:
            for column in DBColumn.objects.filter(db_table=fk_table):
                self.columns += fk_table.db_schema.name + '.' + fk_table.name + '.' + column.name + ' AS ' + fk_table.name + '_' + column.name + ', '

        self.columns = self.columns[:-2]

        return self.columns

    def prepare_joins(self):
        self.joins = ''

        for fk_table in self.fk_tables:
            self.joins += ' LEFT JOIN ' \
                          + fk_table.db_schema.name + '.' + fk_table.name + \
                          ' ON ' \
                          + fk_table.db_schema.name + '.' + fk_table.name + '.' + fk_table.primary_key + \
                          ' = ' \
                          + self.main_table.db_schema.name + '.' + self.main_table.name + '.' + fk_table.fk_name
