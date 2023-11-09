from tortoise import Tortoise, fields, run_async
from tortoise.models import Model

"""
Each user can create only one container.
Only one container for a ctf can be created from a team.
Container:
    id (pk)
    name
    ctf_id
    ports           # stored as csv
    team_id
    user_id
    flag            # TBD

CTF:
    id (pk)
    name
    image_name
    image_config
"""

# No relationships yet
class Container(Model):
    id: str      = fields.TextField(pk=True)
    name: str    = fields.TextField()
    ctf_id: int  = fields.IntField()
    ports: str   = fields.TextField()
    team_id: int = fields.IntField()
    user_id: int = fields.IntField()
    flag: str    = fields.TextField()

class CTF(Model):
    name: str         = fields.TextField()
    image_name: str   = fields.TextField()
    image_config: str = fields.TextField()


# Might want to keep the schemas and init in separate files
async def init():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={'models': ['pwncore.db']}
    )
    await Tortoise.generate_schemas()
run_async(init())
