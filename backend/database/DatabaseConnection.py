import psycopg2


class DatabaseConnection:
    def __init__(self, db_config):
        self.db_config = db_config

        template_db = "host='{host}' dbname='{dbname}' user='{user}' password='{password}'"

        db_string = template_db.format(
            host=self.db_config.host,
            dbname=self.db_config.name,
            user=self.db_config.user_db,
            password=self.db_config.password_db,
        )

        self.db_pgconn = psycopg2.connect(db_string)
