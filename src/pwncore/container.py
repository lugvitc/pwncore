import sys
import aiodocker
from pwncore.config import config

docker_client: aiodocker.Docker = None  # type: ignore[assignment]

if not hasattr(sys, "_is_a_test"):
    docker_client = aiodocker.Docker(url=config.docker_url)
