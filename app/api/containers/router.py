import docker

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import Containers

from app.api.containers.containersRepo import ContainersRepo
from app.api.repositiries.repositoriesRepo import RepositoriesRepo
from app.api.repositiries.versionRepo import VersionRepo
from app.api.users.userRepo import UserRepo


class ContainersRouter():
   def __init__(self):
      self.client = docker.from_env()

      self.containersRepo = ContainersRepo()
      self.repositoriesRepo = RepositoriesRepo()
      self.versionRepo = VersionRepo()
      self.userRepo = UserRepo()

      self.router = APIRouter()

      self.router.post("/", status_code=200)(self.containersCreation)
      self.router.post("/{id}/start", status_code=200)(self.containersStart)
      self.router.post("/{id}/stop", status_code=200)(self.containersStop)
      self.router.post("/{id}/restart", status_code=200) (self.containersRestart)
      self.router.delete("/{id}", status_code=200)(self.containersDelete)
      self.router.get("/", status_code=200)(self.containersList)
      self.router.get("/{id}", status_code=200)(self.containersInfo)


   async def containersCreation(self, data: Containers, request: Request):
      
      user_id = self.userRepo.getInfo(request)['user_id']

      repo_info = self.repositoriesRepo.get(
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
         mes = self.versionRepo.get(
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


      if self.containersRepo.check({'containers_name':container_name}, user_id):
         raise HTTPException(status_code=400, detail='Контейнер уже существует')


      container = self.containersRepo.clone(repo_url, data.version, base_dir, image_name, container_name)

      info = container.attrs

      repositories_data = {
         'user_id': user_id,
         'containers_name': container_name,
         'repositories_id': data.repositories_id,
         'version': data.version
      }
      
      self.containersRepo.create(data=repositories_data)

      return {"message": f"Контейнер {info} успешно запущен"}

                                        
   async def containersStart(self, id, request: Request):
      user_id = self.userRepo.getInfo(request)['user_id']
      
      if not self.containersRepo.check({'id':id}, user_id):
         raise HTTPException(status_code=400, detail='Контейнер не существует')
      
      res = self.containersRepo.get(
            conditions={'id':id,
                        'user_id': user_id,
            }
      )
      
      container = self.client.containers.get(res[0]['containers_name'])
      container.start

      return {"message": "Контейнер успешно запущен"}

                                           
   async def containersStop(self, id, request: Request):

      user_id = self.userRepo.getInfo(request)['user_id']

      if not self.containersRepo.check({'id':id}, user_id):
         raise HTTPException(status_code=400, detail='Контейнер не существует')
      
      res = self.containersRepo.get(
            conditions={'id':id,
                        'user_id': user_id,
            }
      )
      
      container = self.client.containers.get(res[0]['containers_name'])
      container.stop()

      return {"message": "Контейнер успешно остановлен"}


   async def containersRestart(self, id, request: Request):

      user_id = self.userRepo.getInfo(request)['user_id']

      if not self.containersRepo.check({'id':id}, user_id):
         raise HTTPException(status_code=400, detail='Контейнер не существует')
      
      res = self.containersRepo.get(
            conditions={'id':id,
                        'user_id': user_id,
            }
      )
      
      container = self.client.containers.get(res[0]['containers_name'])
      container.restart()

      return {"message": "Контейнер успешно перезапущен"}

                                           
   async def containersDelete(self, request: Request, id):

      user_id = self.userRepo.getInfo(request)['user_id']

      if not self.containersRepo.check({'id':id}, user_id):
         raise HTTPException(status_code=400, detail='Контейнер не существует')
      
      res = self.containersRepo.get(
            conditions={'id':id,
                        'user_id': user_id,
            }
      )
      
      container = self.client.containers.get(res[0]['containers_name'])
      container.stop()
      container.remove()

      self.containersRepo.delete(id=id)

      return {"message": "Контейнер успешно удален"}

                                               
   async def containersList(self, request: Request):
      user_id = self.userRepo.getInfo(request)['user_id']

      mes = self.containersRepo.get(
         conditions={'user_id': user_id}
      )
         
      return JSONResponse(mes)

                                                
   async def containersInfo(self, id, request: Request):

      user_id = self.userRepo.getInfo(request)['user_id']

      if not self.containersRepo.check({'id':id}, user_id):
         raise HTTPException(status_code=400, detail='Контейнер не существует')
      
      res = self.containersRepo.get(
            conditions={'id':id,
                        'user_id': user_id,
            }
      )
      
      container = self.client.containers.get(res[0]['containers_name'])
      info = container.attrs

      return JSONResponse(info)