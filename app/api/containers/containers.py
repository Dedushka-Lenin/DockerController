import docker
import os
import git

from git import Repo

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import Containers

from app.api.users import auxiliary_functions as users_functions
from app.api.containers import auxiliary_functions as containers_functions

####################################################################################################

def set_control_table(control_table):
   global controlTable
   controlTable = control_table

   global client
   client = docker.from_env()

   global containersFunctions
   containersFunctions = containers_functions
   containersFunctions.set_control_table(controlTable, client)

   global usersFunctions
   usersFunctions = users_functions
   usersFunctions.set_control_table(controlTable)

####################################################################################################

router = APIRouter()

# Создание нового контейнера из репозитория
@router.post("/", status_code=200)
async def containers_creation(data: Containers, request: Request):
   
   user_id = usersFunctions.getUserInfo(request)['user_id']

   repo_info = controlTable.fetchRecordTable(
      table_name='repositories',
      conditions={'id': data.repositories_id}
   )

   if repo_info == []:
      raise HTTPException(status_code=401, detail=f'id - {data.repositories_id} не существует')

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
         raise HTTPException(status_code=400, detail='Несуществующая версия')
      
      else:
         base_dir = f'./repo/{repo_name}/{data.version}'
         image_name = f'{repo_name}:{data.version}'
         container_name = f'{user_id}.{repo_name}.{data.version}'


   mes = controlTable.fetchRecordTable(
      table_name='containers',
      conditions={'containers_name': container_name,
                  'user_id': user_id,
      }
   )
   
   containers_list = client.containers.list(all=True)
   container_exists = any(container.name == container_name for container in containers_list)

   if mes != [] and container_exists:
      raise HTTPException(status_code=400, detail='Контейнер уже существует')


   container = containersFunctions.clone_container(repo_url, data.version, base_dir, image_name, container_name)

   info = container.attrs

   repositories_data = {
      'user_id': user_id,
      'containers_name': container_name,
      'repositories_id': data.repositories_id,
      'version': data.version
   }
   
   controlTable.createRecordTable(table_name='containers', data=repositories_data)

   return {"message": f"Контейнер {info} успешно запущен"}

# Запуск контейнера
@router.post("/{id}/start", status_code=200)                                               
async def containersStart(id, request: Request):
   user_id = usersFunctions.getUserInfo(request)['user_id']

   if not containersFunctions.сhecking_container(id, user_id):
      raise HTTPException(status_code=400, detail='Контейнер не существует')

   container = client.containers.get(id)

   container.start

   return {"message": "Контейнер успешно запущен"}

# Остановка контейнера
@router.post("/{id}/stop", status_code=200)                                                
async def containersStop(id, request: Request):

   user_id = usersFunctions.getUserInfo(request)['user_id']

   if not containersFunctions.сhecking_container(id, user_id):
      raise HTTPException(status_code=400, detail='Контейнер не существует')

   container = client.containers.get(id)
   container.stop()

   return {"message": "Контейнер успешно остановлен"}

# Перезапуск контейнера
@router.post("/{id}/restart", status_code=200)                                             
async def containersRestart(id, request: Request):

   user_id = usersFunctions.getUserInfo(request)['user_id']

   if not containersFunctions.сhecking_container(id, user_id):
      raise HTTPException(status_code=400, detail='Контейнер не существует')

   container = client.containers.get(id)
   container.restart()

   return {"message": "Контейнер успешно перезапущен"}

# Удаление котейнера
@router.delete("/{id}", status_code=200)                                                   
async def containersDelete(request: Request, id):

   user_id = usersFunctions.getUserInfo(request)['user_id']

   if not containersFunctions.сhecking_container(id, user_id):
      raise HTTPException(status_code=400, detail='Контейнер не существует')

   container = client.containers.get(id)
   container.stop()
   container.remove()

   controlTable.deleteRecordTable(table_name='containers', id=id)

   return {"message": "Контейнер успешно удален"}

# Получение списка контейнеров
@router.get("/", status_code=200)                                                          
async def containersList(request: Request):
   user_id = usersFunctions.getUserInfo(request)['user_id']

   mes = controlTable.fetchRecordTable(
      table_name='containers',
      conditions={'user_id': user_id}
   )
      
   return JSONResponse(mes)

# Получение информации о контейнере
@router.get("/{id}", status_code=200)                                                      
async def containersInfo(id, request: Request):

   user_id = usersFunctions.getUserInfo(request)['user_id']

   if not containersFunctions.сhecking_container(id, user_id):
      raise HTTPException(status_code=400, detail='Контейнер не существует')
   
   container = client.containers.get(id)
   info = container.attrs

   return JSONResponse(info)