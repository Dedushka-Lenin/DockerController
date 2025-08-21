import psycopg2


from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql

from app.models.schemas import ConnectDBConf

class ControlDB:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, connect_conf: ConnectDBConf , autocommit: bool = False):
        """Устанавливает соединение с базой данных и создает курсор."""

        self.connection = psycopg2.connect(
            dbname=connect_conf['dbname'],
            user=connect_conf['user'],
            password=connect_conf['password'],
            host=connect_conf['host'],
            port=connect_conf['port']
        )

        self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.connection.autocommit = autocommit
        self.cursor = self.connection.cursor()

        return self.connection, self.cursor

    def close(self):
        """Закрывает соединение и курсор."""

        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def check_database_exists(self, db_name: str) -> bool:
        """Проверяет, существует ли база данных с именем db_name."""

        query = "SELECT 1 FROM pg_database WHERE datname=%s"
        self.cursor.execute(query, (db_name,))
        exists = self.cursor.fetchone()

        return exists is not None

    def create_database(self, db_name: str):
        """Создает новую базу данных с именем db_name."""

        create_query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
        self.cursor.execute(create_query)