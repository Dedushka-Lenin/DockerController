import docker

from fastapi import HTTPException

from app.db.record_manager import RecordManager


class ContainersRepo(RecordManager):
    def __init__(self):
        super().__init__("containers")
        self.client = docker.from_env()

    def get(self, id: int, user_id: int) -> dict:
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
