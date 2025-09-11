import jwt

from dynaconf import Dynaconf

from fastapi import HTTPException

from app.db.record_manager import RecordManager


class UserRepo(RecordManager):
    def __init__(self):
        super().__init__("users")

        self.settings = Dynaconf(settings_files=["jwt_conf.toml"])

    def get(self, request):

        token = request.cookies.get("access_token")

        if not token:
            raise HTTPException(status_code=401, detail="Нет аунтификации")

        try:
            payload = jwt.decode(
                token, self.settings.SECRET_KEY, algorithms=[self.settings.ALGORITHM]
            )
            login = payload.get("sub")
            if login is None:
                raise HTTPException(status_code=401, detail="Неверный токен")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Токен просрочен")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Неверный токен")

        if not super().check(conditions={"login": login}):
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        res = super().get(conditions={"login": login})

        return res[0]
