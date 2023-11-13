from tortoise import fields
from tortoise.models import Model

# Tortoise is initiated from __main__.py since initiating
# it as a submodule creates multiple event loops.

# No relationships yet
class Container(Model):
    id: str      = fields.TextField(pk=True)
    name: str    = fields.TextField()
    ctf_id: int  = fields.IntField()
    ports: str   = fields.TextField()
    team_id: int = fields.IntField()
    flag: str    = fields.TextField()

class CTF(Model):
    name: str         = fields.TextField()
    image_name: str   = fields.TextField()
    image_config: str = fields.TextField()
