import signal
import sys

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dynaconf import Dynaconf


class DbConnector:
    _instance = None
    _cursor = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_cursor(self):
        if not self._cursor:
            connect_conf = Dynaconf(settings_files=["connect_conf.toml"])

            self.connect(connect_conf)
            self._initialized = True

        return self._cursor

    def connect(self, connect_conf):

        self.connection = psycopg2.connect(
            dbname=connect_conf["dbname"],
            user=connect_conf["user"],
            password=connect_conf["password"],
            host=connect_conf["host"],
            port=connect_conf["port"],
        )

        self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.connection.autocommit = True
        self._cursor = self.connection.cursor()

        signal.signal(signal.SIGINT, self.handle_sigint)

    def handle_sigint(self, signum, frame):
        self.close()
        sys.exit(0)

    def close(self):
        if hasattr(self, "cursor") and self._cursor:
            self._cursor.close()
        if hasattr(self, "connection") and self.connection:
            self.connection.close()
