import docker

client = docker.from_env()

print(client.containers.run("fedora", "echo hello world"))
print(client.containers.run("bfirsh/reticulate-splines", detach=True))
print(client.containers.list())

# container = client.containers.get('725bd1ee76dd')

# print(container)

# print(container.logs())

# print(container.stop())

# for line in container.logs(stream=True):
#     print(line.strip())

# print(client.images.pull('nginx'))

# print(client.images.list())


# print(client.configs.list())