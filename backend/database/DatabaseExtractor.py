from pygrametl.datasources import SQLSource
from .DatabaseConnection import DatabaseConnection


class DatabaseExtractor(DatabaseConnection):
    def __init__(self, db_config):
        super(DatabaseExtractor, self).__init__(db_config=db_config)


    def extract_tables(self, search, schemas):
        """
        Extracts all the tables from a database
        :param search: The key work to compare with the tables names
        :param schemas: The schema to search at
        :return: A list() of tables that match with the search
        """
        schemas_where_statement = DatabaseExtractor.prepare_schemas_where_statement(schemas)

        query = "SELECT \
                 table_name, table_schema \
                FROM information_schema.tables \
                WHERE table_name LIKE '%" + search + "%' AND " + schemas_where_statement + ";"

        return list(SQLSource(connection=self.db_pgconn, query=query))

    @staticmethod
    def prepare_schemas_where_statement(schemas):
        where_statement = "( "

        for schema in schemas:
            where_statement += "table_schema = '" + schema.name + "' OR "

        where_statement = where_statement[:-3]
        where_statement += ")"

        return where_statement
