import aiodocker
import atexit
import asyncio

docker_client = aiodocker.Docker()


async def docker_cleanup():
    await docker_client.close()

atexit.register(lambda: asyncio.run(docker_cleanup()))
