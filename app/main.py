import uvicorn
import docker
import os
import signal
import sys
import requests
import subprocess
import psycopg2
import git

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql

from git import Repo

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

db_name = 'containersDB'

# Проверка существования базы данных
cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (db_name,))
exists = cursor.fetchone()

if not exists:
    # Создание базы данных, если её нет
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))

connection = psycopg2.connect(
   dbname=db_name,
   user=USER,
   password=PASSWORD,
   host=HOST,
   port=PORT
)

connection.autocommit = True

cursor = connection.cursor()

connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

####################################################################################################

def signal_handler(signum, frame):
    cursor.close()
    connection.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

####################################################################################################

app = FastAPI()

client = docker.from_env()

controlTable = ControlTable(cursor=cursor)

####################################################################################################

controlTable.createTable(table_name="users", 
                        fields= [
                           ('login', 'VARCHAR(255)', 'NOT NULL CHECK (LENGTH(login) >= 3)'),
                           ('password', 'VARCHAR(255)', 'NOT NULL CHECK (LENGTH(password) >= 6)')
                           ]
                     )

controlTable.createTable(table_name="containers", 
                        fields= [
                           ('user_id', 'INTEGER', 'NOT NULL'),
                           ('repositories_id', 'INTEGER', 'NOT NULL'),
                           ('version', 'VARCHAR(255)', 'NOT NULL')
                           ],
                     )

controlTable.createTable(table_name="repositories", 
                        fields= [
                           ('user_id', 'INTEGER', 'NOT NULL'),
                           ('url', 'VARCHAR(255)', 'NOT NULL'),
                           ('name', 'VARCHAR(255)', 'NOT NULL'),
                           ('description', 'VARCHAR(255)', 'NOT NULL')
                           ]
                     )

controlTable.createTable(table_name="version", 
                        fields= [
                           ('repositories_id', 'INTEGER', 'NOT NULL'),
                           ('version', 'VARCHAR(255)', 'NOT NULL')
                           ],
                     )

####################################################################################################

class User(BaseModel):

   login: str = Field(min_length=3)
   password: str = Field(min_length=6)


class Containers(BaseModel):

   repositories_id: int
   version: str = Field(default_factory='')


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
async def containersCreation(data:Containers):

   repo_info = controlTable.fetchRecordTable(
      table_name='repositories', 
      conditions={
         'id':data.repositories_id
         }
      )

   # Клонирование репозитория
   repo_url = repo_info[0]['url']

   base_dir = f'./repo/{repo_info[0]["name"]}/{data.version}'

   image_name = 'my_custom_image:latest'  # Имя и тег образа
   container_name = f'15111'  # Имя контейнера

   # Шаг 1: Клонируем репозиторий (если нужно)
   if not os.path.exists(base_dir):
      # Попытка клонировать с указанием ветки
      try:
         git.Repo.clone_from(
               url=repo_url,
               to_path=base_dir,
               branch=data.version,
               depth=1
         )
      except git.exc.GitCommandError as e:
         # Если ветка не найдена, клонируем без указания ветки
         print(f"Ветка '{data.version}' не найдена. Клонирование без указания ветки.")
         git.Repo.clone_from(
               url=repo_url,
               to_path=base_dir,
               depth=1
         )

   else:
      print("Репозиторий уже клонирован.")

   # Шаг 2: Создаем клиент Docker
   client = docker.from_env()

   # Шаг 3: Строим образ из клонированного репозитория
   print("Строим Docker-образ...")
   image, logs = client.images.build(path=base_dir, tag=image_name)

   # Вывод логов сборки (опционально)
   for log in logs:
      if 'stream' in log:
         print(log['stream'].strip())

   # Шаг 4: Запускаем контейнер из образа
   print("Запускаем контейнер...")

   container = client.containers.run(image_name, name=container_name, detach=True)

   print(f"Контейнер '{container_name}' запущен.")

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
async def repositoriesCreation(url:str):

   user_id = '123456789'

   parts = url.rstrip('/').split('/')
   owner = parts[-2]
   repo = parts[-1]

   api_url = f"https://api.github.com/repos/{owner}/{repo}"

   response = requests.get(api_url)
   if response.status_code == 200:
      data = response.json()

      description = data.get('description', 'Нет описания')
      full_name = data.get('full_name', '')
      html_url = data.get('html_url', '')
      print(f"Репозиторий: {full_name}")
      print(f"Описание: {description}")
      print(f"URL: {html_url}")
   
      # Выполняем команду для получения тегов по URL
      result = subprocess.run(
         ['git', 'ls-remote', '--tags', url],
         capture_output=True,
         text=True,
         check=True
      )
      lines = result.stdout.strip().split('\n')
      tags = []
      for line in lines:
         parts = line.split()
         if len(parts) == 2:
               ref = parts[1]
               # ref выглядит как refs/tags/v1.0.0
               if ref.startswith('refs/tags/'):
                  tag_name = ref[len('refs/tags/'):]
                  tags.append(tag_name)

      print(tags)

   repositories_data = {
      'user_id':user_id,
      'url': url,
      'name':full_name,
      'description': description
   }

   message = controlTable.creatingRecordTable(table_name='repositories', data=repositories_data)

   for version in tags:

      repositories_version_data = {
         'repositories_id':message['id'],
         'version':version
      }

      controlTable.creatingRecordTable(table_name='version', data=repositories_version_data)

   

@repositories.get("/", status_code=200)                                                        # Список репозиториев
async def repositoriesList():

   user_id = '123456789'

   result = controlTable.fetchRecordTable(
      table_name='repositories', 
      conditions={
         'user_id':user_id
         }
      )

   return result

@repositories.get("/{id}", status_code=200)                                                    # Вывод информации о репозитории
async def repositoriesInfo(id):

   user_id = '123456789'

   result = controlTable.fetchRecordTable(
      table_name='repositories', 
      conditions={
         'id':id,
         'user_id':user_id
         }
      )

   return result

####################################################################################################

app.include_router(users)
app.include_router(containers)
app.include_router(repositories)

####################################################################################################


if __name__ == "__main__":
    uvicorn.run("main:app")