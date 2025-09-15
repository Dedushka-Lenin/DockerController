import os

from dynaconf import Dynaconf
from fastapi import HTTPException

class ConfAdapter:
    def __init__(self):
        connect_conf_path = "app/core/config/connect_conf.toml"
        jwt_conf_path = "app/core/config/jwt_conf.toml"

        self.check(connect_conf_path)
        self.check(jwt_conf_path)

        self.connect_conf = Dynaconf(settings_files=[connect_conf_path])
        self.jwt_conf = Dynaconf(settings_files=[jwt_conf_path])

    def check(self, path):
        if not os.path.exists(path):
            raise HTTPException(status_code=400, detail="Отсутствуют файлы конфигурации")

    def get_connect_conf(self):
        return self.connect_conf
    
    def get_jwt_conf(self):
        return self.jwt_conf
    

