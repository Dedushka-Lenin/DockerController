import signal
import sys

import psycopg2
import psycopg2.pool
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app.core.config import CONNECT_CONF



class DbConnector:
    _instance = None
    _cursor = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("Создается новый экземпляр DbConnector")
            cls._instance = super().__new__(cls)
        else:
            print("Используется существующий экземпляр DbConnector")
        return cls._instance
    
    
    def connect(self, connect_conf = CONNECT_CONF):

        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=1,
            dbname=connect_conf['dbname'],
            user=connect_conf['user'],
            password=connect_conf['password'],
            host=connect_conf['host'],
            port=connect_conf['port']
        )

        self.connection = self.connection_pool.getconn()

        self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.connection.autocommit = True
        self._cursor = self.connection.cursor()

        print(f'подключение открыто : {self._cursor}')
        
        signal.signal(signal.SIGINT, self.handle_sigint)

    
    def get_cursor(self):
        if not self._cursor:
            self.connect()
            self._initialized = True

        return self._cursor


    def handle_sigint(self, signum, frame):
        print("Получен сигнал SIGINT")
        self.close()
        sys.exit(0)


    def close(self):
        if hasattr(self, 'cursor') and self._cursor:
            self._cursor.close()
            print('Курсор закрыт')
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            print('Соединение закрыто')
        if self.connection_pool:
            self.connection_pool.closeall
            print("Пул соединений PostgreSQL закрыт")
