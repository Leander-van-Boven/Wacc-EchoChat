from typing import Dict, List
from uuid import UUID

from app.schemas import BaseSchema
from app.schemas.message import MessageSchema
from app.schemas.room import RoomSchema


class SearchResultSchema(BaseSchema):
    total: int


class MessagesSearchResultSchema(SearchResultSchema):
    results: Dict[UUID, List[MessageSchema]]


class RoomsSearchResultSchema(SearchResultSchema):
    results: List[RoomSchema]
