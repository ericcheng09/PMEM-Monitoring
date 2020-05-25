import docker
#   https://docker-py.readthedocs.io/en/stable/containers.html
try:
    client = docker.APIClient("unix://var/run/docker.sock")
    containers = client.containers(all=True)
    for container in containers:
        print('docker_status,Id={} status="{}"'.format(container["Id"], container["Status"]))
except Exception as e:
    print(e)

