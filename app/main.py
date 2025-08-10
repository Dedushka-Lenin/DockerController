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
                           ('containers_name', 'VARCHAR(255)', 'NOT NULL'),
                           ('repositories_id', 'INTEGER', 'NOT NULL'),
                           ('version', 'VARCHAR(255)', 'NOT NULL')
                           ],
                     )

controlTable.createTable(table_name="repositories", 
                        fields= [
                           ('user_id', 'INTEGER', 'NOT NULL'),
                           ('url', 'VARCHAR(255)', 'NOT NULL'),
                           ('repositories_name', 'VARCHAR(255)', 'NOT NULL'),
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

   # Получить список всех контейнеров (запущенных и остановленных)
   containers = client.containers.list(all=True)

   # Вывести информацию о каждом контейнере
   for container in containers:

      container_list.append({
         'id': container.id,
         'name':container.name,
         'status':container.status
         }
      )
      
   return JSONResponse(container_list)

@containers.post("/", status_code=200)                                                         # Создание нового контейнера из репозитория
async def containers_creation(data: Containers):
   
   user_id = '123456789'

   repo_info = controlTable.fetchRecordTable(
      table_name='repositories',
      conditions={'id': data.repositories_id}
   )

   if repo_info == []:
      return JSONResponse(content={'message':f'id - {data.repositories_id} не существует'}, status_code=400)

   repo_info = repo_info[0]
   repo_url = repo_info['url']
   repo_name = repo_info['repositories_name']


   if data.version == '':
      base_dir = f'./repo/{repo_name}'
      image_name = f'{repo_name}'
      container_name = f'{user_id}.{repo_name}'

   else:
      mes = controlTable.fetchRecordTable(
      table_name='version', 
      conditions={
         'version':data.version,
         'repositories_id':data.repositories_id
         }
      )
      
      if mes == []:
         return JSONResponse(content={'message':'Несуществующая версия'}, status_code=400)
      
      else:
         base_dir = f'./repo/{repo_name}/{data.version}'
         image_name = f'{repo_name}:{data.version}'
         container_name = f'{user_id}.{repo_name}.{data.version}'

   mes = controlTable.fetchRecordTable(
      table_name='containers',
      conditions={'containers_name': container_name}
   )

   cont = client.containers.list(all=True)

   # Проверить наличие контейнера с нужным именем
   container_exists = any(c.name == container_name for c in cont)

   if mes != [] and container_exists:
      return {"message": "Контейнер уже существует"}

   if not os.path.exists(base_dir):
      if data.version == '':
         git.Repo.clone_from(
            url=repo_url,
            to_path=base_dir,
            depth=1
         )

      else:
         git.Repo.clone_from(
            url=repo_url,
            to_path=base_dir,
            branch=data.version,
            depth=1
         )

   client.images.build(path=base_dir, tag=image_name)

   container = client.containers.run(image_name, name=container_name, detach=True)
   info = container.attrs

   repositories_data = {
      'user_id': user_id,
      'containers_name': container_name,
      'repositories_id': data.repositories_id,
      'version': data.version
   }
   
   controlTable.creatingRecordTable(table_name='containers', data=repositories_data)

   return {"message": f"Контейнер {info} успешно запущен"}

@containers.get("/{name}", status_code=200)                                                      # Получение информации о контейнере
async def containersInfo(name):

   mes = controlTable.fetchRecordTable(
      table_name='containers',
      conditions={'containers_name': name}
   )

   if mes == []:
      return {"message": "Контейнер не существует"}
   
   container = client.containers.get(name)
   info = container.attrs

   return JSONResponse(info)

@containers.post("/{name}/start", status_code=200)                                               # Запуск контейнера
async def containersStart(name):

   mes = controlTable.fetchRecordTable(
      table_name='containers',
      conditions={'containers_name': name}
   )

   if mes == []:
      return {"message": "Контейнер не существует"}

   container = client.containers.get(name)

   container.status

   container.start

   return {"message": "Контейнер успешно запущен"}
   
@containers.post("/{name}/stop", status_code=200)                                                # Остановка контейнера
async def containersStop(name):

   container = client.containers.get(name)
   container.stop()

   return {"message": "Контейнер успешно остановлен"}

@containers.post("/{name}/restart", status_code=200)                                             # Перезапуск контейнера
async def containersRestart(name):

   container = client.containers.get(name)
   container.restart()

   return {"message": "Контейнер успешно перезапущен"}

@containers.delete("/{name}", status_code=200)                                                   # Удаление котейнера
async def containersDelete(name):

   container = client.containers.get(name)
   container.remove()

   return {"message": "Контейнер успешно удален"}


####################################################################################################
# Блок работы с репозиториями и пользователями


repositories = APIRouter(prefix="/repositories", tags=["repositories"])


@repositories.post("/", status_code=200)                                                       # Добавление нового репозитоория
async def repositoriesCreation(url:str):

   user_id = '123456789'

   mes = controlTable.fetchRecordTable(
      table_name='repositories', 
      conditions={
         'user_id':user_id,
         'url':url
         }
      )
   
   if mes != []:
      return {"message": "Репозиторий уже существует"}

   parts = url.rstrip('/').split('/')
   owner = parts[-2]
   repo = parts[-1]

   api_url = f"https://api.github.com/repos/{owner}/{repo}"

   response = requests.get(api_url)
   if response.status_code == 200:
      data = response.json()

      description = data.get('description', 'Нет описания')
      full_name = data.get('full_name', '')
   
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

      repositories_data = {
         'user_id':user_id,
         'url': url,
         'repositories_name':full_name.replace('/','.'),
         'description': description
      }

      message = controlTable.creatingRecordTable(table_name='repositories', data=repositories_data)

      for version in tags:

         repositories_version_data = {
            'repositories_id':message['id'],
            'version':version
         }

         controlTable.creatingRecordTable(table_name='version', data=repositories_version_data)

      return {"message": "Репозиторий успешно записан"}
   
   return {"message": "Некорректная ссылка"}

   

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