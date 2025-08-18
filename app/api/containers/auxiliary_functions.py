import os

from git import Repo

from app.control_db.control_table import ControlTable

class ContainersFunctions():
    def __init__(self, cursor, client):
        self.controlTable = ControlTable(cursor)
        self.client = client

    def сheckingContainer(self, filtr, user_id):

        mes = self.controlTable.fetchRecordTable(
            table_name='containers',
            conditions={**{
                        'user_id': user_id,
            }, **filtr}
        )

        if mes == []:
            return False
        
        containers_list = self.client.containers.list(all=True)
        container_exists = any(container.name == mes[0]["containers_name"] for container in containers_list)

        if container_exists:
            return True

        return False

    def cloneContainer(self, repo_url, version, base_dir, image_name, container_name):

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