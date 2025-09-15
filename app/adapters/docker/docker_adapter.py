import os
import docker

from git import Repo


class DockerAdapter:
    def __init__(self):
        self.client = docker.from_env()

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
