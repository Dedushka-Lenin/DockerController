import requests
import subprocess

from fastapi import APIRouter, HTTPException, Request

from app.api.users.auxiliary_functions import UserFctions
from app.control_db.control_table import ControlTable

####################################################################################################

class RepositoriesRouter():
   def __init__(self, cursor):
      self.controlTable = ControlTable(cursor)
      self.userFctions = UserFctions(cursor)

      self.router = APIRouter()

      self.router.post("/", status_code=200) (self.repositoriesCreation)
      self.router.get("/", status_code=200) (self.repositoriesList)
      self.router.get("/{id}", status_code=200) (self.repositoriesInfo)

   # Добавление нового репозитоория
   async def repositoriesCreation(self, url:str, request: Request):

      user_id = self.userFctions.getUserInfo(request)['user_id']

      mes = self.controlTable.fetchRecordTable(
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

         message = self.controlTable.createRecordTable(table_name='repositories', data=repositories_data)

         for version in tags:

            repositories_version_data = {
               'repositories_id':message['id'],
               'version':version
            }

            self.controlTable.createRecordTable(table_name='version', data=repositories_version_data)

         return {"message": "Репозиторий успешно записан"}
      
      raise HTTPException(status_code=400, detail="Некорректная ссылка")

   # Функция вывода списка репозиторие
   async def repositoriesList(self, request: Request):

      user_id = self.userFctions.getUserInfo(request)['user_id']

      print(user_id)

      result = self.controlTable.fetchRecordTable(
         table_name='repositories', 
         conditions={
            'user_id':user_id
            }
         )

      return result

   # Функция вывода информации о репозитории
   async def repositoriesInfo(self, id, request: Request):

      user_id = self.userFctions.getUserInfo(request)['user_id']

      result = self.controlTable.fetchRecordTable(
         table_name='repositories', 
         conditions={
            'id':id,
            'user_id':user_id
            }
         )
      
      if result == []:
         raise HTTPException(status_code=400, detail="Репозитория с таким id не существует")

      return result