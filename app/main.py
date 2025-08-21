import uvicorn
import signal
import sys

from fastapi import FastAPI

from app.control_db.control_db import ControlDB
from app.control_db.control_table import ControlTable

from app.core.config import DBNAME, USER, PASSWORD, HOST, PORT

from app.core.tables import tables

from app.api.containers.router import ContainersRouter
from app.api.repositiries.router import RepositoriesRouter
from app.api.users.router import UserRouter




сontrolDB = ControlDB()

connection, cursor = сontrolDB.connect(
                        connect_conf={
                        'dbname': 'postgres',
                        'user': USER,
                        'password': PASSWORD,
                        'host': HOST,
                        'port': PORT
                        },
                        autocommit=True
                    )

exists = сontrolDB.check_database_exists(DBNAME)
if not exists:
    сontrolDB.create_database(DBNAME)

connection, cursor = сontrolDB.connect(
                        connect_conf={
                        'dbname': DBNAME,
                        'user': USER,
                        'password': PASSWORD,
                        'host': HOST,
                        'port': PORT
                        },
                        autocommit=True
                    )


сontrolTable = ControlTable(cursor)

for table_name in tables.keys():
   сontrolTable.createTable(
      table_name=table_name, 
      fields=tables[table_name]
   )

containersRouter = ContainersRouter(cursor)
repositoriesRouter = RepositoriesRouter(cursor)
userRouter = UserRouter(cursor)

app = FastAPI()
app.include_router(containersRouter.router, prefix="/containers", tags=["containers"])
app.include_router(repositoriesRouter.router, prefix="/repositories", tags=["repositories"])
app.include_router(userRouter.router, tags=["users"])


def signal_handler(signum, frame):
   сontrolDB.close()
   sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
   uvicorn.run("app.main:app")