import asyncio
from datetime import datetime
import logging
from typing import Optional, Any
from uuid import UUID, uuid4

from cassandra.cqlengine import CQLEngineException
from distributed_websocket import Connection
from distributed_websocket._message import Message as WSMessage
from distributed_websocket._connection import Connection
from fastapi import HTTPException
from redis.exceptions import ConnectionError
from starlette.websockets import WebSocket

from app.models import Room
from app.util import check_redis_connection, setup_websocket_manager
from app.routers.dependencies import ensure_cassandra_connection
from app.schemas.message import MessageSchema
from app.models import Message as CassandraMessage, User

WS_MANAGER_CONNECTED = True

websocket_manager = setup_websocket_manager()

error_data = {
    'type': 'send',
    'data': {
        'action': 'error',
        'message': 'An error occurred while handling websocket action'
    }
}


def send_error_message(topic: str | UUID, message: str):
    """
    Sends an error message to the user
    :param topic: the user to send the message to
    :param message: the error message
    """
    message = WSMessage.from_client_message(data={
        **error_data,
        'topic': str(topic),
        'data': {
            **error_data['data'],
            'message': message
        }
    })
    logging.warning('Websocket %s: trying to send error message: %s', topic, message)
    # no need to send this message to the broker, as we know the user is connected to this websocket server
    websocket_manager.send(message)


async def add_new_message(connection: Connection, msg: dict, user: User):
    """
    Adds a new message to the database and sends it to the other users in the room over the websocket
    (if they are connected)
    :param connection: the connection that sent the message
    :param msg: the message to add
    :param user: the user that sent the message
    :return: None
    """
    try:
        msg_data = msg['data']

        await ensure_cassandra_connection()

        # Convert the message to a Cassandra ORM object, and meanwhile save it
        message_orm = CassandraMessage.create(
            uuid=uuid4(),
            sender_id=msg_data['userId'],
            room_id=msg_data['roomId'],

            content=msg_data['content'],
            username=user.username,

            reply_message=msg_data['replyMessage'],
            message_stamp=datetime.utcnow().time(),
            message_date=datetime.utcnow().date(),
            index_id=datetime.utcnow(),
            saved=True
        )

        # Convert ORM model to a dictionary
        message_schema = MessageSchema.from_orm(message_orm).dict(by_alias=True)
        # Convert non-string types to string
        message_schema['_id'] = str(message_schema['_id'])
        message_schema['indexId'] = message_schema['indexId'].strftime('%Y-%m-%d %H:%M:%S.%f')
        message_schema['senderId'] = str(message_schema['senderId'])
        message_schema['date'] = message_schema['date'].strftime('%d-%m-%Y')
        message_schema['time_stamp'] = message_schema['time_stamp'].strftime('%H:%M:%S')

        # Send the message to the other users in the room
        room_id = UUID(msg_data['roomId'])
        room = Room.nodes.get(uuid=room_id.hex)

        for destination_user in room.users:
            data = {
                'type': 'send', 'topic': str(destination_user.uuid), 
                'data': {
                    'action': 'new_message', 
                    'roomId': str(room_id),
                    'message': message_schema
                }
            }
            logging.info('Message %s: sending new_message message to user %s', message_orm.uuid, destination_user.uuid)
            # Send the message to the user, if they are not connected this function will do nothing
            await websocket_manager.receive(connection, data)

    except (CQLEngineException, ValueError, HTTPException, ConnectionError) as e:  # (hopefully) catch database (connection) errors
        user_uuid = UUID(user.uuid)
        logging.error('Websocket %s: error while saving message to database: %s', user_uuid, e)
        send_error_message(user_uuid, 'An error occurred while handling the new message')


async def update_message_seen(connection: Connection, msg: dict, user: User):
    """
    Updates the message seen property in the database and sends it to the other users in the room over the websocket
    :param connection: the connection that sent the message
    :param msg: the message to update
    :param user: the user that sent the message
    :return: None
    """
    try:
        await ensure_cassandra_connection()

        msg_data = msg['data']
        room_id = UUID(msg_data['roomId'])
        index_id = datetime.strptime(msg_data['messageIndex'], '%Y-%m-%d %H:%M:%S.%f')
        message_id = msg_data['messageId']

        # Obtain the message from the database
        message_orm = CassandraMessage.filter(room_id=room_id).filter(index_id=index_id).get(uuid=message_id)
        # Update the seen (and distributed) property
        message_orm.distributed = True  # if its seen, that surely it has been received as well
        message_orm.seen = True
        message_orm.save()
        logging.info('Message %s: updated message seen', message_id)

        # Send the message to the other users in the room
        room = Room.nodes.get(uuid=room_id.hex)
        for destination_user in room.users:
            data = {
                'type': 'send', 'topic': str(destination_user.uuid), 
                'data': {
                    'action': 'message_update',
                    'roomId': str(room_id),
                    'messageId': str(message_orm.uuid),
                    'props': {
                        'distributed': True,
                        'seen': True
                    }
                }
            }
            logging.info('Message %s: sending update_message_seen to %s', message_id, destination_user.uuid)
            await websocket_manager.receive(connection, data)
        
    except (CQLEngineException, ValueError, ConnectionError) as e:  # (hopefully) catch database (connection) errors
        logging.error('Websocket %s: error while updating message seen: %s', user.uuid, e)
        send_error_message(str(user.uuid), 'An error occurred while handling the message seen event')


async def send_user_status_change(connection: Connection, user: User, status: str):
    """
    Sends a user status change message to all the users connected to any room the user is in
    """
    user_uuid = UUID(user.uuid)
    try:
        data = {
            'type': 'send',
            'data': {
                'action': 'user_update',
                'userId': str(user_uuid),
                'props': {
                    'status': status
                }
            }
        }

        # Send the message to all the users in the rooms the user is in
        # Use a set to avoid sending the message to the same user twice
        destination_user_uuids = set([usr.uuid for room in user.rooms for usr in room.users])
        
        for destination_user_uuid in destination_user_uuids:
            logging.info(
                'User %s: sending user_status_change with status %s message to %s',
                user_uuid,
                status, 
                destination_user_uuid
            )
            await websocket_manager.receive(connection, {**data, 'topic': str(destination_user_uuid)})

    except (ValueError, ConnectionError) as e:
        logging.error('Websocket %s: error while sending user status change: %s', user_uuid, e)
        send_error_message(user_uuid, 'An error occurred while handling the user status change event')


async def handle_message(connection: Connection, msg, user: User):
    """
    Async wrapper around the message handlers
    :param msg: the message to handle
    :param user: the user that sent the message
    :return: None
    """
    if msg['type'] == 'send':
        if msg['topic'] == 'new_message':
            await add_new_message(connection, msg, user)
        elif msg['topic'] == 'message_seen':
            await update_message_seen(connection, msg, user)
    elif msg['type'] == 'user_status_change':
        await send_user_status_change(connection, user, msg['data']['new_status'])


async def websocket_endpoint(
    ws: WebSocket,
    conn_id: str,
    *,
    topic: Optional[Any] = None
) -> None:
    """
    Main websocket endpoint, handles the connection and the messages.

    We assume that the `conn_id` is the user's uuid. We will set the topic of the connection to the user's uuid, so that
    we can send messages to the user by sending them to the topic with the user's uuid.

    An embedded 'topic' property (`action`) will then be used to determine what to do with the message by the receiver.

    :param ws: the websocket connection
    :param conn_id: the connection id
    :param topic: the topic of the connection
    :return:
    """

    global websocket_manager, WS_MANAGER_CONNECTED

    # TODO: add JWT to websocket connection and check if user is authenticated

    # Obtain the user from the database, for validation and caching purposes
    user = User.get_user_by_id(uuid=UUID(conn_id).hex)
    if user is None:
        logging.warning('Websocket %s: could not find user for websocket connection', conn_id)
        await ws.close()
        return

    connection: Connection = await websocket_manager.new_connection(ws, conn_id, topic=conn_id)
    logging.info('Websocket %s: accepted new connection', connection.id)
    # Send user online to other users that have a connection with the user
    await asyncio.create_task(
        handle_message(connection, {'type': 'user_status_change', 'data': {'new_status': 'online'}}, user)
    )
    
    async for msg in connection.iter_json():
        logging.info('Websocket %s: Got new message', connection.id)

        redis_connected = await check_redis_connection()
        if not redis_connected:
            WS_MANAGER_CONNECTED = False
            logging.error('Websocket %s: Redis connection lost', connection.id)
            await ws.send_json({
                **error_data,
                'data': {
                    **error_data['data'],
                    'message': 'Redis connection lost'
                }
            })
            continue
        elif not WS_MANAGER_CONNECTED and redis_connected:
            # Redis connection restored, reconnect the websocket manager
            try:
                await websocket_manager.shutdown()
            except:
                pass
            logging.warning('Redis: trying to reconnect to Redis')
            websocket_manager = setup_websocket_manager()
            await websocket_manager.startup()
            WS_MANAGER_CONNECTED = True
            logging.warning('Redis: reconnected to Redis')

        await asyncio.create_task(handle_message(connection, msg, user))

    try:
        logging.info('Websocket %s: closing websocket connection', connection.id)
        # Send user offline to other users that have a connection with the user
        await asyncio.create_task(
            handle_message({'type': 'user_status_change', 'data': {'new_status': 'offline'}}, user)
        )
        await websocket_manager.remove_connection(connection)
    except:
        pass
