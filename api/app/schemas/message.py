from datetime import datetime, date, time
from uuid import UUID

from pydantic import Field

from app.schemas import BaseSchema


class MessageSchema(BaseSchema):
    uuid: UUID = Field(alias='_id')
    index_id: datetime
    content: str

    sender_id: UUID
    username: str | None
    avatar: str | None = 'https://avatars.githubusercontent.com/u/16872793?v=4'

    date: date | str
    stamp: time | str = Field(alias='time_stamp')

    saved: bool = False
    distributed: bool = False
    seen: bool = False
    deleted: bool = False
    failure: bool = False

    disable_actions: bool = False
    disable_reactions: bool = False

    reply_message: 'MessageSchema' or None = None

    files: list = []
    reactions: list = []

    class Config:
        json_encoders = {
            date: lambda d: d.strftime('%d-%m-%Y'),
        }


class MessageFetchSchema(BaseSchema):
    messages: list[MessageSchema] = []
    count: int = 0
    paging_state: str | None = None
