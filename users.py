import jwt
from dynaconf import Dynaconf
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Response, Request

from app.models.schemas import User
from app.repo.users_repo import UserRepo


class UserRouter:
    def __init__(self):
        self.userRepo = UserRepo()

        self.settings = Dynaconf(settings_files=["jwt_conf.toml"])
        self.pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        self.router = APIRouter()

        self.router.post("/register", status_code=200)(self.register)
        self.router.post("/login", status_code=200)(self.login)
        self.router.get("/users/info", status_code=200)(self.info)

    async def register(self, user: User):
        if self.userRepo.check(conditions={"login": user.login}):
            raise HTTPException(
                status_code=400, detail="Пользователь с таким именем уже существует"
            )

        hashed_password = self.pw_context.hash(user.password)

        self.userRepo.create(data={"login": user.login, "password": hashed_password})

        return {"message": "Пользователь успешно создан"}

    async def login(self, response: Response, user: User):
        if not self.userRepo.check(conditions={"login": user.login}):
            raise HTTPException(status_code=400, detail="Неверные имя или пароль")

        res = self.userRepo.get(conditions={"login": user.login})

        user_hashed_pw = res[0]["password"]

        if not self.pw_context.verify(user.password, user_hashed_pw):
            raise HTTPException(status_code=400, detail="Неверные имя или пароль")

        expire = datetime.utcnow() + timedelta(
            minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"sub": user.login, "exp": expire}
        token = jwt.encode(
            to_encode, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM
        )

        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=60 * self.settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            samesite="lax",
        )

        return {"message": "Успешный вход в аккаунт"}

    async def info(self, request: Request):
        res = self.userRepo.get(request)

        del res["password"]

        return res
