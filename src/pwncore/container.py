import aiodocker
from pwncore.config import config

docker_client = aiodocker.Docker(url=config.docker_url)
