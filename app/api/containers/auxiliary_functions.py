import os
import git

from git import Repo

def set_control_table(control_table, Client):
   global controlTable
   global client
   controlTable = control_table
   client = Client

####################################################################################################

def сhecking_container(id, user_id):
   mes = controlTable.fetchRecordTable(
      table_name='containers',
      conditions={'id': id,
                  'user_id': user_id,
      }
   )

   if mes == []:
       return False
   
   containers_list = client.containers.list(all=True)
   container_exists = any(container.name == mes[0]['containers_name'] for container in containers_list)

   if container_exists:
      return True

   return False

def clone_container(repo_url, version, base_dir, image_name, container_name):

    if not os.path.exists(base_dir):
        if version == '':
            git.Repo.clone_from(
                url=repo_url,
                to_path=base_dir,
                depth=1
            )

        else:
            git.Repo.clone_from(
                url=repo_url,
                to_path=base_dir,
                branch=version,
                depth=1
            )

    client.images.build(path=base_dir, tag=image_name)

    container = client.containers.run(image_name, name=container_name, detach=True)

    return container