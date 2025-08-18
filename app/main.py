import uvicorn
import signal
import sys

from fastapi import FastAPI


from app.control_db import init_db

initDB = init_db

cursor = initDB.cursor
connection = initDB.connection

def signal_handler(signum, frame):
   cursor.close()
   connection.close()
   sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

from app.api.containers.router import ContainersRouter
from app.api.repositiries.router import RepositoriesRouter
from app.api.users.router import UserRouter

containersRouter = ContainersRouter(cursor)
repositoriesRouter = RepositoriesRouter(cursor)
userRouter = UserRouter(cursor)


app = FastAPI()

app.include_router(containersRouter.router, prefix="/containers", tags=["containers"])
app.include_router(repositoriesRouter.router, prefix="/repositories", tags=["repositories"])
app.include_router(userRouter.router, tags=["users"])


if __name__ == "__main__":
    uvicorn.run("main:app")