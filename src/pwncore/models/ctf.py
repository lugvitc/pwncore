from __future__ import annotations

from tortoise.models import Model
from tortoise import fields
from tortoise.fields import Field


class CTF(Model):
    name = fields.TextField()
    image_name = fields.TextField()
    image_config: Field[dict[str, list]] = fields.JSONField()  # type: ignore[assignment]


# reveal_type(CTF().image_config)
