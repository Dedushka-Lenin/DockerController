import psycopg2


from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql

from app.models.schemas import ConnectDBConf

class ControlDB():
    # Функция потключения к базе данных
    def connectDB(self, connectConf:ConnectDBConf, autocommit:bool = False):

        connection = psycopg2.connect(
            dbname=connectConf['dbname'],
            user=connectConf['user'],
            password=connectConf['password'],
            host=connectConf['host'],
            port=connectConf['port']
        )

        connection.autocommit = autocommit

        self.cursor = connection.cursor()

        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        return connection, self.cursor


    # Функция проверки существования базы дынных
    def checkingDB(self, db_name):
        self.cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (db_name,))
        exists = self.cursor.fetchone()

        return exists


    # Функция создания базы данных
    def createDB(self, db_name):
        self.cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))