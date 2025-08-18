import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Response, Request

from app.models.schemas import User
from app.api.users.auxiliary_functions import UserFctions
from app.control_db.control_table import ControlTable
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


class UserRouter():
   def __init__(self, cursor):
      self.controlTable = ControlTable(cursor)
      self.userFctions = UserFctions(cursor)
      self.pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

      self.router = APIRouter()

      self.router.post("/register", status_code=200)(self.register)
      self.router.post("/login", status_code=200)(self.login)
      self.router.get("/users/info", status_code=200)(self.usersInfo)

   async def register(self, user: User):
      # Проверка существования пользователя
      res = self.controlTable.fetchRecordTable(
         table_name='users', 
         conditions={'login': user.login}
      )

      if res != []:
         raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
      
      # Хеширование пароля
      hashed_password = self.pw_context.hash(user.password)

      # Создание записи пользователя
      self.controlTable.createRecordTable(table_name='users', data={
         'login': user.login,
         'password': hashed_password
      })

      return {"message": "Пользователь успешно создан"}

   async def login(self, response: Response, user: User):
      # Поиск пользователя по логину
      res = self.controlTable.fetchRecordTable(
         table_name='users', 
         conditions={'login': user.login}
      )

      if res == []:
         raise HTTPException(status_code=400, detail="Неверные имя или пароль")
      
      user_hashed_pw = res[0]["password"]

      # Проверка пароля
      if not self.pw_context.verify(user.password, user_hashed_pw):
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

   async def usersInfo(self, request: Request):
      res = self.userFctions.getUserInfo(request)

      return res