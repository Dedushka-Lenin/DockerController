import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Response, Request, Depends, Body

from app.models.schemas import User
from app.core.config import *

####################################################################################################

def set_control_table(control_table):
    global controlTable
    controlTable = control_table

####################################################################################################

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_info(request: Request):

   token = request.cookies.get("access_token")
   if not token:
      raise HTTPException(status_code=401, detail="Not authenticated")
   
   try:
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      username = payload.get("sub")
      if username is None:
         raise HTTPException(status_code=401, detail="Invalid token")
   except jwt.ExpiredSignatureError:
      raise HTTPException(status_code=401, detail="Token has expired")
   except jwt.PyJWTError:
      raise HTTPException(status_code=401, detail="Invalid token")
   
   # Получение данных пользователя из базы
   res = controlTable.fetchRecordTable(
      table_name='users',
      conditions={'login': username}
   )

   if not res:
      raise HTTPException(status_code=404, detail="User not found")
   
   return {
      "user_id": res[0]['id'],
      "username": username
   }

####################################################################################################

router = APIRouter()

@router.post("/register", status_code=200)
async def register(user: User = Body(...)):
   # Проверка существования пользователя
   res = controlTable.fetchRecordTable(
      table_name='users', 
      conditions={'login': user.login}
   )
   if res != []:
      raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
   # Хеширование пароля
   hashed_password = pwd_context.hash(user.password)
   # Создание записи пользователя
   controlTable.creatingRecordTable(table_name='users', data={
      'login': user.login,
      'password': hashed_password
   })
   return {"message": "Пользователь успешно создан"}



@router.post("/login", status_code=200)
async def login(response: Response, form_data: User = Body(...)):
   # Поиск пользователя по логину
   res = controlTable.fetchRecordTable(
      table_name='users', 
      conditions={'login': form_data.login}
   )

   if res == []:
      raise HTTPException(status_code=400, detail="Incorrect username or password")
   
   user_hashed_pw = res[0]["password"]
   # Проверка пароля
   if not pwd_context.verify(form_data.password, user_hashed_pw):
      raise HTTPException(status_code=400, detail="Incorrect username or password")
   
   # Создаем JWT токен
   expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
   to_encode = {"sub": form_data.login, "exp": expire}
   token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

   # Устанавливаем cookie
   response.set_cookie(
      key="access_token",
      value=token,
      httponly=True,
      max_age=60*ACCESS_TOKEN_EXPIRE_MINUTES,
      samesite="lax"
   )
   
   return {"access_token": token, "token_type": "bearer"}

@router.get("/users/info")
async def usersInfo(request: Request):

   res = get_info(request)
      
   return res
