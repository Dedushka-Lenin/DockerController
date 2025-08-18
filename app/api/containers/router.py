import docker

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import Containers

from app.api.users.auxiliary_functions import UserFctions
from app.api.containers.auxiliary_functions import ContainersFunctions
from app.control_db.control_table import ControlTable


class ContainersRouter():
   def __init__(self, cursor):
      self.client = docker.from_env()
      self.controlTable = ControlTable(cursor)
      self.userFctions = UserFctions(cursor)
      self.containersFunctions = ContainersFunctions(cursor, self.client)

      self.router = APIRouter()

      self.router.post("/", status_code=200)(self.containersCreation)
      self.router.post("/{id}/start", status_code=200)(self.containersStart)
      self.router.post("/{id}/stop", status_code=200)(self.containersStop)
      self.router.post("/{id}/restart", status_code=200) (self.containersRestart)
      self.router.delete("/{id}", status_code=200)(self.containersDelete)
      self.router.get("/", status_code=200)(self.containersList)
      self.router.get("/{id}", status_code=200)(self.containersInfo)


   # Создание нового контейнера из репозитория
   async def containersCreation(self, data: Containers, request: Request):
      
      user_id = self.userFctions.getUserInfo(request)['user_id']

      repo_info = self.controlTable.fetchRecordTable(
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
         mes = self.controlTable.fetchRecordTable(
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


      if self.containersFunctions.сheckingContainer({'containers_name':container_name}, user_id):
         raise HTTPException(status_code=400, detail='Контейнер уже существует')


      container = self.containersFunctions.cloneContainer(repo_url, data.version, base_dir, image_name, container_name)

      info = container.attrs

      repositories_data = {
         'user_id': user_id,
         'containers_name': container_name,
         'repositories_id': data.repositories_id,
         'version': data.version
      }
      
      self.controlTable.createRecordTable(table_name='containers', data=repositories_data)

      return {"message": f"Контейнер {info} успешно запущен"}

   # Запуск контейнера                                              
   async def containersStart(self, id, request: Request):
      user_id = self.userFctions.getUserInfo(request)['user_id']
      if not self.containersFunctions.сheckingContainer({'id':id}, user_id):
         raise HTTPException(status_code=400, detail='Контейнер не существует')
      
      res = self.controlTable.fetchRecordTable(
            table_name='containers',
            conditions={'id':id,
                        'user_id': user_id,
            }
      )
      
      container = self.client.containers.get(res[0]['containers_name'])
      container.start

      return {"message": "Контейнер успешно запущен"}

   # Остановка контейнера                                              
   async def containersStop(self, id, request: Request):

      user_id = self.userFctions.getUserInfo(request)['user_id']

      if not self.containersFunctions.сheckingContainer({'id':id}, user_id):
         raise HTTPException(status_code=400, detail='Контейнер не существует')
      
      res = self.controlTable.fetchRecordTable(
            table_name='containers',
            conditions={'id':id,
                        'user_id': user_id,
            }
      )
      
      container = self.client.containers.get(res[0]['containers_name'])
      container.stop()

      return {"message": "Контейнер успешно остановлен"}

   # Перезапуск контейнера                                         
   async def containersRestart(self, id, request: Request):

      user_id = self.userFctions.getUserInfo(request)['user_id']

      if not self.containersFunctions.сheckingContainer({'id':id}, user_id):
         raise HTTPException(status_code=400, detail='Контейнер не существует')
      
      res = self.controlTable.fetchRecordTable(
            table_name='containers',
            conditions={'id':id,
                        'user_id': user_id,
            }
      )
      
      container = self.client.containers.get(res[0]['containers_name'])
      container.restart()

      return {"message": "Контейнер успешно перезапущен"}

   # Удаление котейнера                                                 
   async def containersDelete(self, request: Request, id):

      user_id = self.userFctions.getUserInfo(request)['user_id']

      if not self.containersFunctions.сheckingContainer({'id':id}, user_id):
         raise HTTPException(status_code=400, detail='Контейнер не существует')
      
      res = self.controlTable.fetchRecordTable(
            table_name='containers',
            conditions={'id':id,
                        'user_id': user_id,
            }
      )
      
      container = self.client.containers.get(res[0]['containers_name'])
      container.stop()
      container.remove()

      self.controlTable.deleteRecordTable(table_name='containers', id=id)

      return {"message": "Контейнер успешно удален"}

   # Получение списка контейнеров                                                     
   async def containersList(self, request: Request):
      user_id = self.userFctions.getUserInfo(request)['user_id']

      mes = self.controlTable.fetchRecordTable(
         table_name='containers',
         conditions={'user_id': user_id}
      )
         
      return JSONResponse(mes)

   # Получение информации о контейнере                                                   
   async def containersInfo(self, id, request: Request):

      user_id = self.userFctions.getUserInfo(request)['user_id']

      if not self.containersFunctions.сheckingContainer({'id':id}, user_id):
         raise HTTPException(status_code=400, detail='Контейнер не существует')
      
      res = self.controlTable.fetchRecordTable(
            table_name='containers',
            conditions={'id':id,
                        'user_id': user_id,
            }
      )
      
      container = self.client.containers.get(res[0]['containers_name'])
      info = container.attrs

      return JSONResponse(info)