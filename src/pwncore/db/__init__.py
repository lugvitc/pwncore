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
    id      = fields.TextField(pk=True)
    name    = fields.TextField()
    ctf_id  = fields.IntField()
    ports   = fields.TextField()
    team_id = field.IntField()
    user_id = field.IntField()
    flag    = field.TextField()

class CTF(Model):
    id              = fields.IntField(pk=True)
    name            = fields.TextField()
    image_name      = field.TextField()
    image_config    = field.TextField()


# Might want to keep the schemas and init in separate files
async def init():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={'models': ['pwncore.db']}
    )
    await Tortoise.generate_schemas()
run_async(init())
