import time

from fastapi import HTTPException
from authlib.jose import jwt, JoseError

from app.repo.token_repo import TokenRepo

from app.adapters.conf.conf_adapter import ConfAdapter


class JWT_Adapter:
    def __init__(self):
        confAdapter = ConfAdapter()
        self.jwt_conf = confAdapter.get_jwt_conf()

        self.tokenRepo = TokenRepo()

    def create(self, data: dict):
        header = {"alg": self.jwt_conf.ALGORITHM}
        payload = {
            **data,
            "exp": int(time.time()) + self.jwt_conf.TOKEN_EXPIRE_MINUTES * 60,
        }
        token = jwt.encode(header, payload, self.jwt_conf.SECRET_KEY)
        return token.decode("utf-8")

    def check(self, token: str):

        if not self.tokenRepo.check({"token": token}):
            raise HTTPException(status_code=400, detail="Нерелевантный токен")

        try:
            claims = jwt.decode(token, self.jwt_conf.SECRET_KEY)
            claims.validate()
            return claims
        except JoseError:

            self.disability(token)

            raise HTTPException(
                status_code=401,
                detail="Недействительный или просроченный токен",
            )

    def disability(self, token):

        self.check(token)

        token_id = self.tokenRepo.get({"token": token})[0]["id"]

        self.tokenRepo.delete(id=token_id)

    def get_id(self, credentials):
        token = credentials.credentials

        claims = self.check(token)

        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Токен не валиден")

        return user_id
