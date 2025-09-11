from pydantic import BaseModel, Field


class User(BaseModel):
    login: str = Field(min_length=3)
    password: str = Field(min_length=6)


class Containers(BaseModel):
    repositories_id: int
    version: str = ""
