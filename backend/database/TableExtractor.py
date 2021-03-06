from pygrametl.datasources import SQLSource
from .DatabaseConnection import DatabaseConnection
from common.models import DBIgnore


class TableExtractor(DatabaseConnection):
    def __init__(self, db_config, name, schema):
        super(TableExtractor, self).__init__(db_config=db_config)

        self.table_name = name
        self.table_schema = schema

        self.special_columns = None

    def get_columns(self, special_columns=True, limit=0):
        """
        Extracts the columns of a table
        :param limit: The limits of columns to extract
        :return: A list() with the names of the columns that match with the search
        """
        query = "SELECT  column_name, data_type, character_maximum_length, numeric_precision, is_nullable \
                FROM information_schema.columns \
                WHERE table_schema = '" + self.table_schema + "' AND table_name = '" + self.table_name + "'"

        if not special_columns and len(self.get_special_columns()) > 0:
            query += " AND " + TableExtractor.not_special_columns_where_statement(self.get_special_columns())

        where_ignore_columns = TableExtractor.get_ignore_columns(self.db_config)

        if where_ignore_columns != '':
            query += " AND " + where_ignore_columns

        if limit > 0:
            query += " LIMIT " + str(limit)

        data = list(SQLSource(connection=self.db_pgconn, query=query))

        return data

    def get_special_columns(self, only_fk=False):
        """
        Extracts all primary and foreing keys columns of a table
        :return: A list() with all the primary and foreing keys columns
        """

        if self.special_columns:
            return self.special_columns

        query = "SELECT \
                    ccu.table_name, \
                    ccu.table_schema, \
                    kc.column_name, \
                    tc.constraint_type \
                FROM information_schema.table_constraints tc \
                JOIN information_schema.key_column_usage kc ON kc.table_name = tc.table_name AND kc.constraint_name = tc.constraint_name \
                JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name \
                WHERE tc.table_name = '" + self.table_name + "' AND tc.table_schema = '" + self.table_schema + "'"

        if only_fk:
            query += " AND tc.constraint_type = 'FOREIGN KEY' AND ccu.table_name != '" + self.table_name + "'"

        self.special_columns = list(SQLSource(connection=self.db_pgconn, query=query))

        return self.special_columns

    def get_data(self, columns, limit=0, offset=0):
        """
        Extract data from a table
        :param columns: The table's columns to have data extracted
        :param limit: The limit of data extracted
        :param offset: The offset to extract the data
        :return: A list() with the data extracted
        """
        if isinstance(columns, list):
            columns = TableExtractor.prepare_columns(columns)

        query = "SELECT " + columns + " FROM " + self.table_schema + "." + self.table_name

        if offset > 0:
            query += " OFFSET " + str(offset)

        if limit > 0:
            query += " LIMIT " + str(limit)

        data = list(SQLSource(connection=self.db_pgconn, query=query))

        sample_list = list()
        for sample_dict in data:
            sample_list.append(sample_dict)

        return sample_list

    def get_primary_key_name(self):
        primary_key_name = ''

        for column in self.special_columns:
            if column.get('constraint_type') == 'PRIMARY KEY':
                primary_key_name = column.get('column_name')
                break

        return primary_key_name

    @staticmethod
    def prepare_columns(columns):
        """
        Transform a list() into a string separeted with commas
        :param columns: A list() with the columns
        :return: A string with the columns
        """
        temp = ''
        for column in columns:
            if isinstance(column, list) or isinstance(column, dict):
                temp += column.get('column_name') + ', '
            else:
                temp += column + ', '

        return temp[:-2]

    @staticmethod
    def not_special_columns_where_statement(special_columns):
        where_statement = " ( "

        for column in special_columns:
            where_statement += "column_name != '" + column.get('column_name') + "' AND "

        where_statement = where_statement[:-4]
        where_statement += " ) "

        return where_statement

    @staticmethod
    def get_ignore_columns(db_config):

        ignore_columns = DBIgnore.objects.filter(ignore_type=DBIgnore.TYPE_COLUMN, db_config=db_config)

        where_ignore_columns = ""

        if ignore_columns.count() > 0:

            where_ignore_columns = " ( "

            for ignore_column in ignore_columns:
                where_ignore_columns += "column_name != '" + ignore_column.name + "' AND "

            where_ignore_columns = where_ignore_columns[:-4]
            where_ignore_columns += " ) "

        return where_ignore_columns
