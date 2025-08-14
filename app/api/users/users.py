import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Response, Request, Body

from app.models.schemas import User
from app.api.users import auxiliary_functions

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

####################################################################################################

def set_control_table(control_table):
   global controlTable
   controlTable = control_table

   global auxiliaryFunctions

   auxiliaryFunctions = auxiliary_functions
   auxiliaryFunctions.set_control_table(controlTable)

####################################################################################################

pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

####################################################################################################

router = APIRouter()

@router.post("/register", status_code=200)
async def register(user: User):
   # Проверка существования пользователя
   res = controlTable.fetchRecordTable(
      table_name='users', 
      conditions={'login': user.login}
   )

   if res != []:
      raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
   
   # Хеширование пароля
   hashed_password = pw_context.hash(user.password)

   # Создание записи пользователя
   controlTable.createRecordTable(table_name='users', data={
      'login': user.login,
      'password': hashed_password
   })

   return {"message": "Пользователь успешно создан"}



@router.post("/login", status_code=200)
async def login(response: Response, user: User):
   # Поиск пользователя по логину
   res = controlTable.fetchRecordTable(
      table_name='users', 
      conditions={'login': user.login}
   )

   if res == []:
      raise HTTPException(status_code=400, detail="Неверные имя или пароль")
   
   user_hashed_pw = res[0]["password"]

   # Проверка пароля
   if not pw_context.verify(user.password, user_hashed_pw):
      raise HTTPException(status_code=400, detail="Неверные имя или пароль")
   
   # Создаем JWT токен
   expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
   to_encode = {"sub": user.login, "exp": expire}
   token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

   # Устанавливаем cookie
   response.set_cookie(
      key="access_token",
      value=token,
      httponly=True,
      max_age=60*ACCESS_TOKEN_EXPIRE_MINUTES,
      samesite="lax"
   )
   
   return {"message": "Успешный вход в аккаунт"}

@router.get("/users/info")
async def usersInfo(request: Request):

   res = auxiliaryFunctions.getUserInfo(request)
      
   return res
