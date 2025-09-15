import jwt

from dynaconf import Dynaconf

from fastapi import HTTPException

from app.db.record_manager import RecordManager


class UserRepo(RecordManager):
    def __init__(self):
        super().__init__("users")
