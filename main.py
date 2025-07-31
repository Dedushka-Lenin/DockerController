import uvicorn
import docker

from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse


####################################################################################################

app = FastAPI()

client = docker.from_env()



####################################################################################################
# Блок работы с пользователем

users = APIRouter(tags=["users"])

@users.post("/register")                                                      # Регистрация нового пользователя
async def register():
   pass

@users.post("/login")                                                         # Вход пользователя
async def login():
   pass

@users.get("/users/info")                                                     # Получение информации о текущем пользователе
async def usersInfo():
   pass


####################################################################################################
# Блок работы с контейнерами


containers = APIRouter(prefix="/containers", tags=["containers"])

@containers.get("/")                                                          # Получение списка контейнеров
async def containersList():


   print(client.containers.run("fedora", "echo hello world"))
   print(client.containers.run("bfirsh/reticulate-splines", detach=True))


   return JSONResponse(client.containers.list())

@containers.post("/")                                                         # Создание контейнера
async def containersCreate():
   return client.containers.create()

@containers.get("/{id}")                                                      # Получение информации о контейнере
async def containersInfo(id):
   return client.containers.get(id)

@containers.post("/{id}/start")                                               # Зпуск контейнера
async def containersStart():
   pass

@containers.post("/{id}/stop")                                                # Остановка контейнера
async def containersStop():
   pass

@containers.post("/{id}/restart")                                             # Перезапуск контейнера
async def containersRestart():
   pass

@containers.delete("/{id}")                                                   # Удаление контейнера
async def containersDelete():
   pass


####################################################################################################
# Блок работы с репозиториями


repositories = APIRouter(prefix="/repositories", tags=["repositories"])

@repositories.post("/")                                                       # 
async def repositoriesCreate():
   pass

@repositories.get("/")                                                        # Получение списка репозиториев
async def repositoriesList():
   pass

@repositories.get("/{id}")                                                    # Получение информации о рипози
async def repositoriesInfo():
   pass


####################################################################################################
# Блок подключения роутеров


app.include_router(users)
app.include_router(containers)
app.include_router(repositories)

####################################################################################################


if __name__ == "__main__":
    uvicorn.run("main:app")