from functools import partial
import logging
import os
from uuid import UUID

from cassandra.cqlengine import connection as cassandra_connection
from fastapi import APIRouter, Depends, Security

from app.models import Message
from app.schemas.message import MessageFetchSchema, MessageSchema
from app.util.authentication import MESSAGE_SCOPES, get_jwt_user
from app.util.cassandra import CASSANDRA_DEFAULT_KEYSPACE, get_messages_pstmt
from app.routers.dependencies import ensure_cassandra_connection

messages_router = APIRouter(
    prefix='/room/{room_id}/message',
    tags=['messages'],
    responses={404: {'description': 'Room Not found'}},
    dependencies=[
        Security(get_jwt_user, scopes=MESSAGE_SCOPES),
        Depends(ensure_cassandra_connection)
    ]
)

message_id_router = APIRouter(
    prefix='/room/{room_id}/message/{message_id}',
    tags=['messages'],
    responses={404: {'description': 'Message Not found'}},
    dependencies=[
        Security(get_jwt_user, scopes=MESSAGE_SCOPES),
        Depends(ensure_cassandra_connection)
    ]
)


@messages_router.get('', response_model=MessageFetchSchema)
async def get_messages(room_id: UUID, c: int = None, ps: str = None):
    """
    Get messages for a room.
    :param room_id: The room to get messages for.
    :param c: (count) How many messages to get.
    :param ps: (paging_state) Used for pagination.
    :return: `MessageFetchSchema`
    """
    global get_messages_pstmt

    count = c
    paging_state = ps

    if not count:
        count = os.environ['DEFAULT_MESSAGE_FETCH_COUNT']
    query = Message.objects.filter(room_id=room_id)

    if get_messages_pstmt is None:
        logging.info('Cassandra: preparing get_messages_pstmt...')
        get_messages_pstmt = cassandra_connection.get_session().prepare(
            f'SELECT * FROM {CASSANDRA_DEFAULT_KEYSPACE}.message WHERE room_id = ? ORDER BY index_id DESC'
        )
    get_messages_pstmt.fetch_size = count

    query = partial(cassandra_connection.get_session().execute,
        get_messages_pstmt, 
        parameters=[room_id],
    )
    if paging_state:
        query = partial(query, paging_state=bytes.fromhex(paging_state))

    results = query()

    def result_to_schema(result):
        result['date'] = result['date'].date().strftime('%d-%m-%Y')
        result['time_stamp'] = result['stamp'].time().strftime('%H:%M:%S')
        return MessageSchema(**result)

    paging_state = results.paging_state
    paging_state_decoded = paging_state.hex() if paging_state else None

    messages = [result_to_schema(result) for result in results.current_rows]

    return MessageFetchSchema(
        messages=messages,
        count=len(messages),
        paging_state=paging_state_decoded
    )
