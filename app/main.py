import uvicorn
import signal
import sys

from fastapi import FastAPI

from app.control_db.control_db import ControlDB
from app.control_db.control_table import ControlTable

from app.core.config import DBNAME, USER, PASSWORD, HOST, PORT

####################################################################################################

controlDB = ControlDB()

connection, cursor = controlDB.connectDB(
                        connectConf={
                           'dbname': 'postgres',
                           'user': USER,
                           'password': PASSWORD,
                           'host': HOST,
                           'port': PORT
                           },
                        autocommit=True
                     )

exists = controlDB.checkingDB(DBNAME)
if not exists:
   controlDB.createDB(DBNAME)

connection, cursor = controlDB.connectDB(
                        connectConf={
                           'dbname': DBNAME,
                           'user': USER,
                           'password': PASSWORD,
                           'host': HOST,
                           'port': PORT
                           },
                        autocommit=True
                     )


controlTable = ControlTable(cursor)

controlTable.createTable(table_name="users", 
                        fields= [
                           {'name': 'login',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL CHECK (LENGTH(login) >= 3)'},

                           {'name': 'password',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL CHECK (LENGTH(password) >= 6)'}
                        ]
                     )

controlTable.createTable(table_name="containers", 
                        fields= [
                           {'name': 'user_id',
                            'dtype': 'INTEGER',
                            'constraints': 'NOT NULL'},
                           {'name': 'containers_name',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL'},
                           {'name': 'repositories_id',
                            'dtype': 'INTEGER',
                            'constraints': 'NOT NULL'},
                           {'name': 'version',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL'}
                        ]
                     )

controlTable.createTable(table_name="repositories", 
                        fields= [
                           {'name': 'user_id',
                            'dtype': 'INTEGER',
                            'constraints': 'NOT NULL'},
                           {'name': 'url',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL'},
                           {'name': 'repositories_name',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL'},
                           {'name': 'description',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL'}
                        ]
                     )

controlTable.createTable(table_name="version", 
                        fields= [
                           {'name': 'repositories_id',
                            'dtype': 'INTEGER',
                            'constraints': 'NOT NULL'},
                           {'name': 'version',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL'}
                        ],
                     )

####################################################################################################

def signal_handler(signum, frame):
    cursor.close()
    connection.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

####################################################################################################

from app.api.containers import containers
from app.api.repositiries import repositiries
from app.api.users import users

Containers = containers
Repositories = repositiries
Users = users

Containers.set_control_table(controlTable)
Repositories.set_control_table(controlTable)
Users.set_control_table(controlTable)

app = FastAPI()

app.include_router(Containers.router, prefix="/containers", tags=["containers"])
app.include_router(Repositories.router, prefix="/repositories", tags=["repositories"])
app.include_router(Users.router, tags=["users"])

####################################################################################################

if __name__ == "__main__":
    uvicorn.run("main:app")