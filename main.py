import uvicorn

from fastapi import FastAPI, APIRouter


####################################################################################################

app = FastAPI()


####################################################################################################
# Блок работы с пользователем

users = APIRouter(tags=["users"])

@users.post("/register")                                                      # Регистрация нового пользователя
async def register():
   pass

@users.post("/login")                                                         # Вход пользователя
async def login():
   pass

@users.get("/users/me")                                                       # Получение информации о текущем пользователе
async def users_me():
   pass


####################################################################################################

containers1 = APIRouter(prefix="/containers", tags=["containers"])

@containers1.get("/")
async def containers():
   pass

@containers1.post("/")
async def containers():
   pass

@containers1.get("/{id}")
async def containers():
   pass

@containers1.post("/{id}/start")
async def containers():
   pass

@containers1.post("/{id}/stop")
async def containers():
   pass

@containers1.post("/{id}/restart")
async def containers():
   pass

@containers1.delete("/{id}")
async def containers():
   pass


####################################################################################################

repositories1 = APIRouter(prefix="/repositories", tags=["repositories"])

@repositories1.post("/")
async def repositories():
   pass

@repositories1.get("/")
async def repositories():
   pass

@repositories1.get("/{id}")
async def repositories():
   pass


####################################################################################################

app.include_router(users)
app.include_router(containers1)
app.include_router(repositories1)

####################################################################################################


if __name__ == "__main__":
    uvicorn.run("main:app")