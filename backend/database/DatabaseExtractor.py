from pygrametl.datasources import SQLSource
from .DatabaseConnection import DatabaseConnection


class DatabaseExtractor(DatabaseConnection):
    def __init__(self, db_config):
        super(DatabaseExtractor, self).__init__(db_config=db_config)

    def get_tables(self, schemas, search=None):
        """
        Extracts all the tables from a database
        :param schemas: The schema to search at
        :param search: The key work to compare with the tables names
        :return: A list() of tables that match with the search
        """
        schemas_where_statement = DatabaseExtractor.prepare_schemas_where_statement(schemas)

        query = "SELECT \
                 table_name, table_schema \
                FROM information_schema.tables \
                WHERE " + schemas_where_statement + " {search} \
                ORDER BY table_name;"

        if search is not None:
            query = query.format(search=search)
        else:
            query = query.format(search="")

        return list(SQLSource(connection=self.db_pgconn, query=query))

    def get_tables_by_words(self, search_words, schemas):
        tables = self.get_tables(schemas)
        final_tables = list()

        print('ALL TALBES: ' + tables.__str__())

        if len(search_words) == 1:
            for table in tables:
                if table.get('table_name').find(search_words[0]) != -1:
                    final_tables.append(table)

        elif len(search_words) == 2:
            order_one = DatabaseExtractor.prepare_possibilities_order_one(search_words)
            order_two = DatabaseExtractor.prepare_possibilities_order_two(search_words)

            for table in tables:
                for word in order_one:
                    if table.get('table_name') == word:
                        final_tables.append(table)

            for table in final_tables:
                tables.remove(table)

            for table in tables:
                for word in order_two:
                    if table.get('table_name').find(word) != -1:
                        final_tables.append(table)

        return final_tables

    @staticmethod
    def prepare_possibilities_order_one(words):
        order_one_matchs = list()

        order_one_matchs.append(words[0] + words[1])
        order_one_matchs.append(words[1] + words[0])

        order_one_matchs.append(words[1] + "_" + words[0])
        order_one_matchs.append(words[0] + "_" + words[1])

        return order_one_matchs

    @staticmethod
    def prepare_possibilities_order_two(words):
        order_two_matchs = list()

        order_two_matchs.append(words[0])
        order_two_matchs.append(words[1])

        return order_two_matchs

    @staticmethod
    def prepare_schemas_where_statement(schemas):
        where_statement = "( "

        for schema in schemas:
            where_statement += "table_schema = '" + schema.name + "' OR "

        where_statement = where_statement[:-3]
        where_statement += ")"

        return where_statement
