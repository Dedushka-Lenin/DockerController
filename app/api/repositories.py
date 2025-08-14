import requests
import subprocess

from fastapi import APIRouter, Request

####################################################################################################

def set_control_table(control_table, users):
   global controlTable
   global Users
   controlTable = control_table
   Users = users

router = APIRouter()

@router.post("/", status_code=200)                                                       # Добавление нового репозитоория
async def repositoriesCreation(url:str, request: Request):

   user_id = Users.get_info(request)['user_id']

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

   

@router.get("/", status_code=200)                                                        # Список репозиториев
async def repositoriesList(request: Request):

   user_id = Users.get_info(request)['user_id']

   result = controlTable.fetchRecordTable(
      table_name='repositories', 
      conditions={
         'user_id':user_id
         }
      )

   return result

@router.get("/{id}", status_code=200)                                                    # Вывод информации о репозитории
async def repositoriesInfo(id, request: Request):

      
   user_id = Users.get_info(request)['user_id']

   result = controlTable.fetchRecordTable(
      table_name='repositories', 
      conditions={
         'id':id,
         'user_id':user_id
         }
      )

   return result