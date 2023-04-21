from typing import List
from uuid import UUID

from app.schemas import BaseSchema


class LoginSchema(BaseSchema):
    username: str
    password: str


class JWTToken(BaseSchema):
    token: str
    token_type: str
    user_uuid: UUID
    is_admin: bool = False


class TokenData(BaseSchema):
    user_uuid: UUID or None = None
    scopes: List[str] = []
