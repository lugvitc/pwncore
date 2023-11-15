from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.exceptions import IntegrityError
from tortoise.models import Model
from tortoise.expressions import Q

if TYPE_CHECKING:
    from pwncore.models.container import Container

__all__ = ("User", "Team", "generate_trigger_script")
# Not too sure here


class User(Model):
    # Registration numbers and other identity tags
    # abstractly just represents one person, expand this
    # field for Identity providers
    tag = fields.CharField(128, unique=True)
    name = fields.CharField(255)
    email = fields.TextField()
    phone_num = fields.CharField(15)

    team: fields.ForeignKeyNullableRelation[Team] = fields.ForeignKeyField(
        "models.Team", "members", null=True, on_delete=fields.OnDelete.SET_NULL
    )

    async def save(self, *args, **kwargs):
        # TODO: Insert/Update in one query
        # Reason why we dont use pre_save: overhead, ugly
        if self.team is not None:
            cnt = await self.team.members.filter(~Q(id=self.pk)).count()
            if cnt >= 3:
                raise IntegrityError("3 or more users already exist for the team")
        return await super().save(*args, **kwargs)


class Team(Model):
    name = fields.CharField(255, unique=True)
    secret_hash = fields.TextField()

    # TODO: Add count constraint somehow, using trigger right now
    members: fields.ReverseRelation[User]
    containers: fields.ReverseRelation[Container]


# Use the trigger if encountering inconsistencies in
# database (shouldn't happen ever tho)

_TRIGGER_SCRIPT_TEMPLATE = """
CREATE OR REPLACE FUNCTION check_max_users_per_team()
RETURNS TRIGGER AS $$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM "user"
        WHERE team_id = NEW.team_id
    ) >= {0} THEN
        RAISE EXCEPTION 'Cannot have more than {0} users in a team';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS max_users_per_team_trigger ON "user";

CREATE TRIGGER max_users_per_team_trigger
BEFORE INSERT OR UPDATE ON "user"
FOR EACH ROW EXECUTE FUNCTION check_max_users_per_team();
"""


def generate_trigger_script(max_users_per_team: int) -> str:
    """Return the trigger script to keep relation between
    :class:`pwncore.models.user.User` and :class:`pwncore.models.user.Team`
    consistent

    Parameters
    ----------
    max_users_per_team : :class:`int`
        Maximum number of users that can be a team

    Returns
    -------
    :class:`str`
        The PostresSQL trigger SQL script

    Raises
    ------
    :class:`TypeError`
        If `max_users_per_team` is not an integer
    """
    # Call at startup and run as script in a transaction
    if not isinstance(max_users_per_team, int):
        raise TypeError(
            f"Expected int but got {type(max_users_per_team)} instance instead"
        )
    return _TRIGGER_SCRIPT_TEMPLATE.format(str(max_users_per_team))
