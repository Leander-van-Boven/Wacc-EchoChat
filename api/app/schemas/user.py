from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas import BaseSchema
from app.models.enums import UserStates

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import User


class UserStateSchema(BaseSchema):
    state: UserStates
    last_changed: datetime


class UserSchema(BaseSchema):
    uuid: UUID = Field(alias='_id')
    username: str
    is_admin: bool = False
    avatar: str | None
    status: UserStateSchema

    @classmethod
    def from_orm(cls, user: 'User', *args, **kwargs) -> 'UserSchema':
        # override the default `from_orm` to add the status field
        res = cls(
            uuid=user.uuid,
            username=user.username,
            is_admin=user.is_admin,
            avatar=user.avatar,
            status=UserStateSchema(**user.get_status()),
        )
        return res
