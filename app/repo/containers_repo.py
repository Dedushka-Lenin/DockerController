import os
import docker

from git import Repo

from fastapi import HTTPException

from app.db.record_manager import RecordManager


class ContainersRepo(RecordManager):
    def __init__(self):
        super().__init__("containers")
        self.client = docker.from_env()

    def _get_container_by_id(self, id: int, user_id: int) -> dict:
        if not super().check({"id": id}, user_id):
            raise HTTPException(status_code=400, detail="Контейнер не существует")
        res = super().get(conditions={"id": id, "user_id": user_id})
        if not res:
            raise HTTPException(status_code=400, detail="Контейнер не найден")
        return res[0]

    def check(self, filtr, user_id):

        if not super().check(
            conditions={
                **{
                    "user_id": user_id,
                },
                **filtr,
            }
        ):
            return False

        containers = super().get(
            conditions={
                **{
                    "user_id": user_id,
                },
                **filtr,
            }
        )

        containers_list = self.client.containers.list(all=True)
        container_exists = any(
            container.name == containers[0]["containers_name"]
            for container in containers_list
        )

        if container_exists:
            return True

        return False

    def clone(self, repo_url: str, base_dir: str, version: str):
        if not os.path.exists(base_dir):
            if version == "":
                Repo.clone_from(url=repo_url, to_path=base_dir, depth=1)
            else:
                Repo.clone_from(url=repo_url, to_path=base_dir, branch=version, depth=1)

    def build(self, base_dir: str, image_name: str, container_name: str):
        self.client.images.build(path=base_dir, tag=image_name)
        container = self.client.containers.run(
            image_name, name=container_name, detach=True
        )
        return container
