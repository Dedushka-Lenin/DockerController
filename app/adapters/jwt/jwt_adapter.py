import time

from fastapi import HTTPException
from authlib.jose import jwt, JoseError

from app.adapters.conf.conf_adapter import ConfAdapter


class JWT_Adapter:
    def __init__(self):
        confAdapter = ConfAdapter()
        self.jwt_conf = confAdapter.get_jwt_conf()

    def create(self, data: dict):
        header = {"alg": self.jwt_conf.ALGORITHM}
        payload = {
            **data,
            "exp": int(time.time()) + self.jwt_conf.TOKEN_EXPIRE_MINUTES * 60,
        }
        token = jwt.encode(header, payload, self.jwt_conf.SECRET_KEY)
        return token.decode("utf-8")

    def verify_jwt(self, token: str):
        try:
            claims = jwt.decode(token, self.jwt_conf.SECRET_KEY)
            claims.validate()
            return claims
        except JoseError:
            raise HTTPException(
                status_code=401,
                detail="Недействительный или просроченный токен",
            )

    def get_user(self, credentials):
        token = credentials.credentials
        claims = self.verify_jwt(token)

        username = claims.get("sub")
        if not username:
            raise HTTPException(status_code=400, detail="Токен не валиден")

        return username
