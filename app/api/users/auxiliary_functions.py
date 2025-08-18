import jwt

from fastapi import HTTPException, Request


from app.control_db.control_table import ControlTable
from app.core.config import SECRET_KEY, ALGORITHM


class UserFctions():
    def __init__(self, cursor):
        self.controlTable = ControlTable(cursor)

    # Функция получения информации о пользователе
    def getUserInfo(self, request: Request):

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
            raise HTTPException(status_code=401, detail="Неверный токе")

        # Получение данных пользователя из базы
        res = self.controlTable.fetchRecordTable(
            table_name='users',
            conditions={'login': login}
        )

        if not res:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        return {
            "user_id": res[0]['id'],
            "login": login
        }