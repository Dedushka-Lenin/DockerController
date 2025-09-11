import requests
import subprocess

from fastapi import APIRouter, HTTPException, Request

from app.repo.repositories_repo import RepositoriesRepo
from app.repo.version_repo import VersionRepo
from app.repo.users_repo import UserRepo


class RepositoriesRouter:
    def __init__(self):

        self.repositoriesRepo = RepositoriesRepo()
        self.versionRepo = VersionRepo
        self.userRepo = UserRepo()

        self.router = APIRouter()

        self.router.post("/", status_code=200)(self.creat)
        self.router.get("/", status_code=200)(self.get)
        self.router.get("/{id}", status_code=200)(self.info)

    async def creat(self, url: str, request: Request):

        user_id = self.userRepo.get(request)["user_id"]

        mes = self.repositoriesRepo.get(conditions={"user_id": user_id, "url": url})

        if mes != []:
            return {"message": "Репозиторий уже существует"}

        parts = url.rstrip("/").split("/")
        owner = parts[-2]
        repo = parts[-1]

        api_url = f"https://api.github.com/repos/{owner}/{repo}"

        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()

            description = data.get("description", "Нет описания")
            full_name = data.get("full_name", "")

            result = subprocess.run(
                ["git", "ls-remote", "--tags", url],
                capture_output=True,
                text=True,
                check=True,
            )

            lines = result.stdout.strip().split("\n")
            tags = []

            for line in lines:
                parts = line.split()
                if len(parts) == 2:
                    ref = parts[1]

                    if ref.startswith("refs/tags/"):
                        tag_name = ref[len("refs/tags/") :]
                        tags.append(tag_name)

            repositories_data = {
                "user_id": user_id,
                "url": url,
                "repositories_name": full_name.replace("/", "."),
                "description": description,
            }

            message = self.repositoriesRepo.create(data=repositories_data)

            for version in tags:

                repositories_version_data = {
                    "repositories_id": message["id"],
                    "version": version,
                }

                self.versionRepo.create(data=repositories_version_data)

            return {"message": "Репозиторий успешно записан"}

        raise HTTPException(status_code=400, detail="Некорректная ссылка")

    async def get(self, request: Request):

        user_id = self.userRepo.get(request)["user_id"]

        result = self.repositoriesRepo.get(conditions={"user_id": user_id})

        return result

    async def info(self, id, request: Request):

        user_id = self.userRepo.get(request)["user_id"]

        result = self.repositoriesRepo.check(conditions={"id": id, "user_id": user_id})

        if not result:
            raise HTTPException(
                status_code=400, detail="Репозитория с таким id не существует"
            )

        return result
