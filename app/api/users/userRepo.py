import jwt

from fastapi import HTTPException

from app.db.recordManager import RecordManager
from app.core.config import SECRET_KEY, ALGORITHM

class UserRepo(RecordManager):
    def __init__(self):
        super().__init__('users')

    def getInfo(self, request):

        token = request.cookies.get("access_token")

        if not token:
            raise HTTPException(status_code=401, detail="Нет аунтификации")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            login = payload.get("sub")
            if login is None:
                raise HTTPException(status_code=401, detail="Неверный токен")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Токен просрочен")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Неверный токен")


        if not super().check(conditions={'login': login}):
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        res = super().get(
            conditions={'login': login}
        )

        return {
            "user_id": res[0]['id'],
            "login": login
        }