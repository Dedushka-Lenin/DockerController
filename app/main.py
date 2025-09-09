import uvicorn

from fastapi import FastAPI

from app.api.containers import ContainersRouter
from app.api.repositories import RepositoriesRouter
from app.api.users import UserRouter



containersRouter = ContainersRouter()
repositoriesRouter = RepositoriesRouter()
userRouter = UserRouter()

app = FastAPI()
app.include_router(containersRouter.router, prefix="/containers", tags=["containers"])
app.include_router(repositoriesRouter.router, prefix="/repositories", tags=["repositories"])
app.include_router(userRouter.router, tags=["users"])



if __name__ == "__main__":
   uvicorn.run("app.main:app")