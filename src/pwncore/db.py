from tortoise import fields
from tortoise.fields import JSONField
from tortoise.models import Model

# Tortoise is initiated from __main__.py since initiating
# it as a submodule creates multiple event loops.

# No relationships yet
class Container(Model):
    id      = fields.TextField(pk=True)
    name    = fields.TextField()
    ctf_id  = fields.IntField()
    ports   = fields.TextField()
    team_id = fields.IntField()
    flag    = fields.TextField()

class CTF(Model):
    name            = fields.TextField()
    image_name      = fields.TextField()
    image_config    = fields.JSONField()
