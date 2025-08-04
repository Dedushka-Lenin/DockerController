import uvicorn
import docker
import os
import signal
import sys
import psycopg2

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql

from git import Repo

from pathlib import Path

from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

from pydantic import BaseModel, Field

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from conf import *
from db.control_db import ControlTable

####################################################################################################

# Подключение к базе данных postgres
connection = psycopg2.connect(
dbname=DBNAME,
user=USER,
password=PASSWORD,
host=HOST,
port=PORT
)

connection.autocommit = True

cursor = connection.cursor()

connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

db_name = 'containersDB'

# Проверка существования базы данных
cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (db_name,))
exists = cursor.fetchone()

if not exists:
    # Создание базы данных, если её нет
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))

####################################################################################################

def signal_handler():
   cursor.close()
   connection.close()

   sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

####################################################################################################

app = FastAPI()

client = docker.from_env()

controlTable = ControlTable(cursor=cursor)

####################################################################################################

class User(BaseModel):

   login: str = Field(min_length=3)
   password: str = Field(min_length=6)

####################################################################################################

controlTable.createTable(table_name="Users", 
                        fields= [
                           ('login', 'VARCHAR(255)', 'NOT NULL CHECK (LENGTH(login) >= 3)'),
                           ('password', 'VARCHAR(255)', 'NOT NULL CHECK (LENGTH(password) >= 6)')
                           ]
                     )

controlTable.createTable(table_name="Containers", 
                        fields= [
                           ('login', 'VARCHAR(255)', 'NOT NULL CHECK (LENGTH(login) >= 3)'),
                           ('password', 'VARCHAR(255)', 'NOT NULL CHECK (LENGTH(password) >= 6)')
                           ],
                        cursor=cursor
                     )

controlTable.createTable(table_name="Repositories", 
                        fields= [
                           ('login', 'VARCHAR(255)', 'NOT NULL CHECK (LENGTH(login) >= 3)'),
                           ('password', 'VARCHAR(255)', 'NOT NULL CHECK (LENGTH(password) >= 6)')
                           ]
                     )

####################################################################################################
# Блок работы с пользователем


users = APIRouter(tags=["users"])

@users.post("/register", status_code=200)                                                      # Регистрация нового пользователя
async def register():
   pass

@users.post("/login", status_code=200)                                                         # Вход пользователя
async def login():
   pass

@users.get("/users/info", status_code=200)                                                     # Получение информации о текущем пользователе
async def usersInfo():
   pass


####################################################################################################
# Блок работы с контейнерами


containers = APIRouter(prefix="/containers", tags=["containers"])


@containers.get("/", status_code=200)                                                          # Получение списка контейнеров
async def containersList():
   container_list = []

   for container in client.containers.list():

      container_list.append(
         {
            'id' : container.id, 
            'name' : container.name, 
            'status' : container.status
            }
         )
      
   return JSONResponse(container_list)

@containers.post("/", status_code=200)                                                         # Создание нового контейнера из репозитория
async def containersCreation():

   container = client.containers.run("bfirsh/reticulate-splines", detach=True)

   info = container.attrs

   return JSONResponse({"message": "контейнер успешно созданн", "info": info})

@containers.get("/{id}", status_code=200)                                                      # Получение информации о контейнере
async def containersInfo(id):
   
   container = client.containers.get(id)
   info = container.attrs

   return JSONResponse(info)

@containers.post("/{id}/start", status_code=200)                                               # Запуск контейнера
async def containersStart(id):
   
   container = client.containers.get(id)
   container.start

   return {"message": "Контейнер успешно запущен"}
   
@containers.post("/{id}/stop", status_code=200)                                                # Остановка контейнера
async def containersStop(id):

   container = client.containers.get(id)
   container.stop()

   return {"message": "Контейнер успешно остановлен"}

@containers.post("/{id}/restart", status_code=200)                                             # Перезапуск контейнера
async def containersRestart(id):

   container = client.containers.get(id)
   container.restart()

   return {"message": "Контейнер успешно перезапущен"}

@containers.delete("/{id}", status_code=200)                                                   # Удаление котейнера
async def containersDelete(id):

   container = client.containers.get(id)
   container.remove()

   return {"message": "Контейнер успешно удален"}


####################################################################################################
# Блок работы с репозиториями и пользователями


repositories = APIRouter(prefix="/repositories", tags=["repositories"])


@repositories.post("/", status_code=200)                                                       # Добавление нового репозитоория
async def repositoriesCreation():
   # # Клонирование репозитория
   # repo_url = 'https://github.com/username/repository.git'
   # local_path = '/path/to/local/repo'

   # Repo.clone_from(repo_url, local_path)

   # # Построение образа
   # client = docker.from_env()
   # image, build_logs = client.images.build(path=local_path, tag='my_image_name')

   # # Запуск контейнера
   # container = client.containers.run('my_image_name', detach=True)

   pass

@repositories.get("/", status_code=200)                                                        # Список репозиториев
async def repositoriesList():
   pass

@repositories.get("/{id}", status_code=200)                                                    # Вывод информации о репозитории
async def repositoriesInfo():
   pass


####################################################################################################

app.include_router(users)
app.include_router(containers)
app.include_router(repositories)

####################################################################################################


if __name__ == "__main__":
    uvicorn.run("main:app")