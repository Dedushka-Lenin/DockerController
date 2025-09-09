import os
import docker

from git import Repo

from app.db.record_manager import RecordManager


class ContainersRepo(RecordManager):
    def __init__(self):
            super().__init__('containers')
            self.client = docker.from_env()


    def check(self, filtr, user_id):

        if not super().check(conditions={**{'user_id': user_id,}, **filtr}): 
            return False

        containers = super().get(
            conditions={**{
                        'user_id': user_id,
            }, **filtr}
        )
        
        containers_list = self.client.containers.list(all=True)
        container_exists = any(container.name == containers[0]["containers_name"] for container in containers_list)

        if container_exists:
            return True

        return False


    def clone(self, repo_url, version, base_dir, image_name, container_name):

        if not os.path.exists(base_dir):
            if version == '':
                Repo.clone_from(
                    url=repo_url,
                    to_path=base_dir,
                    depth=1
                )

            else:
                Repo.clone_from(
                    url=repo_url,
                    to_path=base_dir,
                    branch=version,
                    depth=1
                )

        self.client.images.build(path=base_dir, tag=image_name)

        container = self.client.containers.run(image_name, name=container_name, detach=True)

        return container