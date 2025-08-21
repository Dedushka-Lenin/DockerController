import signal
import sys

import psycopg2

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app.core.config import CONNECT_CONF


class DbConnector:
    def __init__(self):
        self.connect_conf = CONNECT_CONF
        self.connect()

    def connect(self):
        self.connection = psycopg2.connect(
            dbname=self.connect_conf['dbname'],
            user=self.connect_conf['user'],
            password=self.connect_conf['password'],
            host=self.connect_conf['host'],
            port=self.connect_conf['port']
        )

        self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

        signal.signal(signal.SIGINT, self.close)

    def close(self, signum, frame):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

        print('подключение закрыто')

        sys.exit(0)
