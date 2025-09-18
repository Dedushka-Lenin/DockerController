from passlib.context import CryptContext
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.schemas import User
from app.repo.users_repo import UserRepo
from app.repo.token_repo import TokenRepo

from app.adapters.jwt.jwt_adapter import JWT_Adapter


class UserRouter:
    def __init__(self):
        self.userRepo = UserRepo()
        self.tokenRepo = TokenRepo()

        self.jwt_adapter = JWT_Adapter()

        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        self.router = APIRouter()

        self.router.post("/register", status_code=200)(self.register)
        self.router.post("/login", status_code=200)(self.login)
        self.router.post("/logout", status_code=200)(self.logout)
        self.router.get("/users/info", status_code=200)(self.info)

    async def register(self, user: User):

        if self.userRepo.check(conditions={"login": user.login}):
            raise HTTPException(
                status_code=400, detail="Пользователь с таким именем уже существует"
            )

        hashed_password = self.pwd_context.hash(user.password)

        self.userRepo.create(data={"login": user.login, "password": hashed_password})

        return {"message": "Пользователь успешно создан"}

    async def login(self, user_log: User):
        if not self.userRepo.check({"login": user_log.login}):
            raise HTTPException(status_code=400, detail="Неверные логин или пароль")
        
        user_inf = self.userRepo.get({"login": user_log.login})[0]

        if not user_inf or not self.pwd_context.verify(
            user_log.password, user_inf["password"]
        ):
            raise HTTPException(status_code=400, detail="Неверные логин или пароль")
        token = self.jwt_adapter.create({"sub": user_inf["id"]})

        self.tokenRepo.create(token=token, user_id=user_inf["id"])

        return {"access_token": token}

    async def logout(
        self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):
        token = credentials.credentials

        self.jwt_adapter.disability(token)

        return {"Tокен инвалидирован"}

    async def info(
        self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):

        user_id = self.jwt_adapter.get_id(credentials)

        return {"Tокен валиден"}
