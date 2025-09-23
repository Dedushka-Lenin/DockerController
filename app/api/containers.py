import docker

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

from app.models.schemas import Containers
from app.repo.containers_repo import ContainersRepo
from app.repo.repositories_repo import RepositoriesRepo
from app.repo.version_repo import VersionRepo
from app.repo.users_repo import UserRepo

from app.adapters.jwt.jwt_adapter import JWT_Adapter
from app.adapters.docker.docker_adapter import DockerAdapter


class ContainersRouter:
    def __init__(self):
        self.client = docker.from_env()

        self.containersRepo = ContainersRepo()
        self.repositoriesRepo = RepositoriesRepo()
        self.versionRepo = VersionRepo()
        self.userRepo = UserRepo()

        self.jwt_adapter = JWT_Adapter()
        self.dockerAdapter = DockerAdapter()

        self.router = APIRouter()
        self.router.post("/", status_code=200)(self.create)
        self.router.post("/{id}/start", status_code=200)(self.start)
        self.router.post("/{id}/stop", status_code=200)(self.stop)
        self.router.post("/{id}/restart", status_code=200)(self.restart)
        self.router.delete("/{id}", status_code=200)(self.delete)
        self.router.get("/", status_code=200)(self.get)
        self.router.get("/{id}", status_code=200)(self.info)

    async def create(
        self,
        data: Containers,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    ):

        user_id = self.jwt_adapter.get_id(credentials)

        repo_info = self.repositoriesRepo.get(
            {"id": data.repositories_id, "user_id": user_id}
        )[0]

        repo_url = repo_info["url"]
        repo_name = repo_info["repositories_name"]

        if data.version == "":
            base_dir = f"./repo/{repo_name}"
            image_name = repo_name
            container_name = f"{user_id}.{repo_name}"
        else:
            mes = self.versionRepo.get(
                conditions={
                    "version": data.version,
                    "repositories_id": data.repositories_id,
                }
            )
            if not mes:
                raise HTTPException(status_code=400, detail="Несуществующая версия")
            base_dir = f"./repo/{repo_name}/{data.version}"
            image_name = f"{repo_name}:{data.version}"
            container_name = f"{user_id}.{repo_name}.{data.version}"

        if self.containersRepo.check(user_id, {"containers_name": container_name}):
            raise HTTPException(status_code=400, detail="Контейнер уже существует")

        self.dockerAdapter.clone(repo_url, base_dir, data.version)

        container = self.dockerAdapter.build(base_dir, image_name, container_name)
        info = container.attrs

        repositories_data = {
            "user_id": user_id,
            "containers_name": container_name,
            "repositories_id": data.repositories_id,
            "version": data.version,
        }
        self.containersRepo.create(data=repositories_data)

        return {"message": f"Контейнер {info} успешно запущен"}

    async def start(
        self, id: int, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):

        user_id = self.jwt_adapter.get_id(credentials)

        container_name = self.containersRepo.get(id, user_id)["containers_name"]

        container = self.client.containers.get(container_name)
        container.start()

        container.reload()

        status = container.status

        if status == "running":
            return {"message": "Контейнер запущен"}
        else:
            return {"message": f"Контейнер не запущен, статус: {status}"}

    async def stop(
        self, id: int, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):

        user_id = self.jwt_adapter.get_id(credentials)

        container_data = self.containersRepo.get(id, user_id)
        container = self.client.containers.get(container_data["containers_name"])
        container.stop()

        container.reload()

        status = container.status

        if status == "exited":
            return {"message": "Контейнер остановлен"}
        else:
            return {"message": f"Контейнер не остановлен, статус: {status}"}

    async def restart(
        self, id: int, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):

        user_id = self.jwt_adapter.get_id(credentials)

        container_data = self.containersRepo.get(id, user_id)
        container = self.client.containers.get(container_data["containers_name"])
        container.restart()

        container.reload()

        status = container.status

        if status == "running":
            return {"message": "Контейнер перезапущен"}
        else:
            return {"message": f"Контейнер не перезапущен, статус: {status}"}

    async def delete(
        self, id: int, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):

        user_id = self.jwt_adapter.get_id(credentials)

        container_data = self.containersRepo.get(id, user_id)
        container = self.client.containers.get(container_data["containers_name"])
        container.stop()
        container.remove()

        self.containersRepo.delete(id=id)

        return {"message": "Контейнер успешно удален"}

    async def get(
        self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):

        user_id = self.jwt_adapter.get_id(credentials)

        print(user_id)

        containers = self.containersRepo.get_list(user_id=user_id)

        return JSONResponse(containers)

    async def info(
        self, id: int, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ):
        user_id = self.jwt_adapter.get_id(credentials)

        container_data = self.containersRepo.get(id, user_id)
        container = self.client.containers.get(container_data["containers_name"])
        info = container.attrs

        return JSONResponse(info)
