import docker
import os
import git

from git import Repo

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.models.schemas import Containers

####################################################################################################

def set_control_table(control_table, users):
   global controlTable
   global Users
   controlTable = control_table
   Users = users

####################################################################################################

def сhecking_container(container_name, user_id):
   mes = controlTable.fetchRecordTable(
      table_name='containers',
      conditions={'containers_name': container_name,
                  'user_id': user_id,
      }
   )

   cont = client.containers.list(all=True)
   container_exists = any(c.name == container_name for c in cont)

   if mes != [] and container_exists:
      return True

   return False

####################################################################################################

router = APIRouter()
client = docker.from_env()

@router.post("/", status_code=200)                                                         # Создание нового контейнера из репозитория
async def containers_creation(data: Containers, request: Request):
   
   user_id = Users.get_info(request)['user_id']

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

   if сhecking_container(container_name, user_id):
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

@router.post("/{name}/start", status_code=200)                                               # Запуск контейнера
async def containersStart(name, request: Request):
   user_id = Users.get_info(request)['user_id']

   if not сhecking_container(name, user_id):
      return {"message": "Контейнер не существует"}

   container = client.containers.get(name)

   container.status

   container.start

   return {"message": "Контейнер успешно запущен"}
   
@router.post("/{name}/stop", status_code=200)                                                # Остановка контейнера
async def containersStop(name, request: Request):

   user_id = Users.get_info(request)['user_id']

   if not сhecking_container(name, user_id):
      return {"message": "Контейнер не существует"}

   container = client.containers.get(name)
   container.stop()

   return {"message": "Контейнер успешно остановлен"}

@router.post("/{name}/restart", status_code=200)                                             # Перезапуск контейнера
async def containersRestart(name, request: Request):

   user_id = Users.get_info(request)['user_id']

   if not сhecking_container(name, user_id):
      return {"message": "Контейнер не существует"}

   container = client.containers.get(name)
   container.restart()

   return {"message": "Контейнер успешно перезапущен"}

@router.delete("/{name}", status_code=200)                                                   # Удаление котейнера
async def containersDelete(name, request: Request):

   user_id = Users.get_info(request)['user_id']

   if not сhecking_container(name, user_id):
      return {"message": "Контейнер не существует"}

   container = client.containers.get(name)
   container.remove()

   return {"message": "Контейнер успешно удален"}

@router.get("/", status_code=200)                                                          # Получение списка контейнеров
async def containersList(request: Request):
   user_id = Users.get_info(request)['user_id']

   mes = controlTable.fetchRecordTable(
      table_name='containers',
      conditions={'user_id': user_id}
   )


   # container_list = []

   # # Получить список всех контейнеров (запущенных и остановленных)
   # containers = client.containers.list(all=True)

   # # Вывести информацию о каждом контейнере
   # for container in containers:
   #    container_list.append({
   #       'id': container.id,
   #       'name':container.name,
   #       'status':container.status
   #       }
   #    )
      
   return JSONResponse(mes)

@router.get("/{name}", status_code=200)                                                      # Получение информации о контейнере
async def containersInfo(name, request: Request):

   user_id = Users.get_info(request)['user_id']

   mes = controlTable.fetchRecordTable(
      table_name='containers',
      conditions={'containers_name': name,
                  'user_id': user_id,
      }
   )
   
   container = client.containers.get(name)
   info = container.attrs

   return JSONResponse(info)