import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Security

from app.models import Room, User
from app.schemas.room import NewRoomSchema, RoomSchema
from app.util.authentication import get_jwt_user, ROOM_SCOPES

rooms_router = APIRouter(
    prefix='/rooms',
    tags=['rooms'],
    responses={
        409: {'description': 'Room already exists'},
    },
    dependencies=[Security(get_jwt_user, scopes=ROOM_SCOPES)]
)

room_id_router = APIRouter(
    prefix='/rooms/{room_id}', 
    tags=['rooms'],
    responses={
        404: {'description': 'Room Not found'},
    },
    dependencies=[Security(get_jwt_user, scopes=ROOM_SCOPES)]
)


@rooms_router.get('', response_model=List[RoomSchema])
async def get_rooms(user_uuid: UUID = Security(get_jwt_user, scopes=ROOM_SCOPES)):
    """
    Get all rooms for a user. User is determined by the JWT token.
    :param user_uuid: The UUID of the user to get rooms for.
    :return: `List[RoomSchema]`
    """
    user = User.nodes.get(uuid=user_uuid)
    return [RoomSchema.from_orm(room) for room in user.rooms]


@rooms_router.post('', status_code=201, response_model=RoomSchema)
async def create_room(room_details: NewRoomSchema, user_uuid: UUID = Security(get_jwt_user, scopes=ROOM_SCOPES)):
    """
    Create a new room for a user.
    :return: `RoomSchema`
    """
    user = User.nodes.get(uuid=user_uuid)
    existing_room = Room.nodes.get_or_none(room_name=room_details.room_name)
    if existing_room:
        raise HTTPException(status_code=409, detail='Room already exists')
    room = Room(room_name=room_details.room_name)
    room.save()
    room.connected_users.connect(user)

    logging.info('Room %s: created by user %s', room.uuid, user_uuid)
    return RoomSchema.from_orm(room)


@rooms_router.post('/join', response_model=RoomSchema)
async def join_room(room_details: NewRoomSchema, user_uuid: UUID = Security(get_jwt_user, scopes=ROOM_SCOPES)):
    """
    Join a room.
    :param room_details: The details of the room to join.
    :param user_uuid: The UUID of the user to join the room.
    :return: `RoomSchema`
    """
    user = User.nodes.get(uuid=user_uuid)
    room = Room.nodes.get_or_none(room_name=room_details.room_name)
    if not room:
        raise HTTPException(status_code=404, detail='Room not found')
    user.rooms.connect(room)
    logging.info('Room %s: user %s joined room', room.uuid, user_uuid)
    return RoomSchema.from_orm(room)


@room_id_router.post('/leave', status_code=204)
async def leave_room(room_id: UUID, user_uuid: UUID = Security(get_jwt_user, scopes=ROOM_SCOPES)):
    """
    Leave a room.
    :param room_id: The UUID of the room to leave.
    :param user_uuid: The UUID of the user to leave the room.
    :return: `None`
    """
    user = User.nodes.get(uuid=user_uuid)
    room = Room.nodes.get_or_none(uuid=room_id.hex)

    if room is None:
        raise HTTPException(status_code=404, detail='Room not found')

    room.connected_users.disconnect(user)

    logging.info('Room %s: user %s left room', room_id, user_uuid)
    return None
