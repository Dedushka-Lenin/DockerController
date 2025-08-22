import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Response, Request

from app.models.schemas import User
from app.api.users.userRepo import UserRepo
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


class UserRouter():
   def __init__(self):

      self.userRepo = UserRepo()

      self.pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

      self.router = APIRouter()

      self.router.post("/register", status_code=200)(self.register)
      self.router.post("/login", status_code=200)(self.login)
      self.router.get("/users/info", status_code=200)(self.usersInfo)


   async def register(self, user: User):
      if self.userRepo.check(conditions={'login': user.login}):
         raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

      hashed_password = self.pw_context.hash(user.password)

      self.userRepo.create(
         data={
            'login': user.login,
            'password': hashed_password
         }
      )

      return {"message": "Пользователь успешно создан"}


   async def login(self, response: Response, user: User):
      if not self.userRepo.check(conditions={'login': user.login}):
         raise HTTPException(status_code=400, detail="Неверные имя или пароль")
      
      res = self.userRepo.get(
         conditions={'login': user.login}
      )

      user_hashed_pw = res[0]["password"]

      if not self.pw_context.verify(user.password, user_hashed_pw):
         raise HTTPException(status_code=400, detail="Неверные имя или пароль")
      
      expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
      to_encode = {"sub": user.login, "exp": expire}
      token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

      response.set_cookie(
         key="access_token",
         value=token,
         httponly=True,
         max_age=60*ACCESS_TOKEN_EXPIRE_MINUTES,
         samesite="lax"
      )
      
      return {"message": "Успешный вход в аккаунт"}


   async def usersInfo(self, request: Request):
      res = self.userRepo.getInfo(request)

      return res