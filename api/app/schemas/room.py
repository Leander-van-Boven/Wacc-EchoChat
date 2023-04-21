from datetime import datetime
import random
from typing import List
from uuid import UUID

from pydantic import Field

from app.schemas import BaseSchema
from app.schemas.message import MessageSchema
from app.schemas.user import UserSchema


def generate_room_avatar() -> str:
    gender = random.choice(['men', 'woman'])
    return f'https://randomuser.me/api/portraits/{gender}/{random.randint(0, 99)}.jpg'


class NewRoomSchema(BaseSchema):
    room_name: str = Field(..., min_length=1, max_length=255)


class RoomSchema(BaseSchema):
    uuid: UUID = Field(alias='roomId')
    room_name: str
    unread_count: int
    index: datetime
    last_message: MessageSchema | None
    users: List[UserSchema]
    typing_users: List[UserSchema]
    avatar: str = Field(default_factory=generate_room_avatar)
