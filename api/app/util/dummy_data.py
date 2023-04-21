import logging
from datetime import datetime
from time import sleep
from uuid import uuid4, UUID

from app.models import Room, User, UserStatus, Message
from app.models.enums import UserStates
from app.util.authentication import get_password_hash


def add_dummy_rooms():
    # Add 5 rooms
    for i in range(5):
        name = f'Room-{i}'
        if Room.nodes.get_or_none(room_name=name) is None:
            Room(room_name=name).save()
            logging.info('Created dummy room: %s', name)


def add_admin_user():
    # Create admin user
    if User.nodes.get_or_none(username='admin') is None:
        User(
            uuid=uuid4().hex,
            username='admin',
            hashed_password=get_password_hash('admin'),
            is_admin=True,
        ).save()
        logging.info('Neo4j: created dummy admin user')


def add_dummy_users():
    # Add 10 normal users
    for i in range(10):
        username = f'Jochie-{i}'
        room = Room.nodes.get(room_name=f'Room-{i // 2}')
        if User.nodes.get_or_none(username=username) is None:
            user = User(username=username, hashed_password=get_password_hash('password'))
            if i == 0:
                user.uuid = UUID('00000000-0000-4000-a000-000000000000').hex
            user.save()
            user.status_rel.connect(UserStatus.nodes.get(state=UserStates.OFFLINE.value))
            user.rooms.connect(room, {})
            logging.info('Created dummy user: %s', username)


def add_dummy_messages(count: int = 10):
    while len(Room.nodes.all(lazy=True)) < 5:
        logging.info('Waiting for rooms to be created...')
        sleep(5)
    while len(User.nodes.all(lazy=True)) < 10:
        logging.info('Waiting for users to be created...')
        sleep(5)

    for i in range(5):
        room = Room.nodes.get(room_name=f'Room-{i}')
        users = room.connected_users
        if len(users) < 2:
            logging.error('Not enough users in room %s', room.room_name)
            continue

        for j in range(count):
            user = users[j % 2]
            message = Message.create(
                uuid=uuid4(),
                index_id=datetime.utcnow(),
                room_id=room.uuid,
                content=f'[{j}] Hello Room {room.room_name}!',
                sender_id=user.uuid,
                username=user.username,
                saved=True,
                distributed=True,
                seen=True,
                message_date = datetime.utcnow().date(),
                message_stamp = datetime.utcnow().time(),
            )
            logging.info('Created dummy message: %s', message)
