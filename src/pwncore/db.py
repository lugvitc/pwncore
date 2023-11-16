from __future__ import annotations

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
    ports: fields.ReverseRelation[Ports]
    team_id = fields.IntField()
    flag    = fields.TextField()

class CTF(Model):
    name            = fields.TextField()
    # docker_config   = fields.JSONField()
    image_name      = fields.TextField()
    image_config    = fields.JSONField()

class Ports(Model):
    container: fields.ForeignKeyRelation[Container] = fields.ForeignKeyField(
        "models.Container", related_name="ports", on_delete=fields.OnDelete.CASCADE
    )
    port = fields.IntField(pk=True)
