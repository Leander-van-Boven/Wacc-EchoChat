from datetime import datetime
from itertools import groupby
from uuid import UUID

from fastapi import APIRouter, Security

from app.models import User, Message
from app.schemas.message import MessageSchema
from app.schemas.room import RoomSchema
from app.schemas.search import MessagesSearchResultSchema, RoomsSearchResultSchema
from app.util.authentication import MESSAGE_SCOPES, ROOM_SCOPES, get_jwt_user
from app.util.elasticsearch import es as elasticsearch_client, message_index

search_messages_router = APIRouter(
    prefix='/search/messages',
    tags=['search'],
    dependencies=[Security(get_jwt_user, scopes=MESSAGE_SCOPES)]
)

search_rooms_router = APIRouter(
    prefix='/search/rooms',
    tags=['search'],
    dependencies=[Security(get_jwt_user, scopes=ROOM_SCOPES)]
)


@search_messages_router.get('/content', response_model=MessagesSearchResultSchema)
async def search_messages_by_content(c: str, user_uuid: UUID = Security(get_jwt_user, scopes=MESSAGE_SCOPES)):
    """
    Search messages by content, only within rooms the user is a member of.
    :param c: The content to search for
    :param user_uuid: The user's uuid, derived from the JWT token
    :return: `MessagesSearchResultSchema`
    """
    user = User.nodes.get(uuid=user_uuid)
    allowed_rooms = [str(UUID(room.uuid)) for room in user.rooms.all()]
    
    body = {
        'query': {
            'bool': {
                'must': [
                    {
                        'query_string': {
                            'query': f'*{c}*',
                            'fields': ['content']
                        }
                    },
                    {'terms': {'room_id': allowed_rooms}}
                ]
            }
        }
    }
    search_results = await elasticsearch_client.search(
        index=message_index,
        body=body
    )
    result_count = search_results['hits']['total']

    if result_count == 0:
        return MessagesSearchResultSchema(
            results={},
            total=0
        )
    
    def create_message_schema(hit: dict) -> MessageSchema:
        hit['message_date'] = datetime.strptime(hit['date'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
        hit['message_stamp'] = hit['stamp']
        hit['index_id'] = datetime.strptime(hit['index_id'], '%Y-%m-%dT%H:%M:%S.%fZ')
        msg = Message(**hit)
        return MessageSchema.from_orm(msg)

    results = {
        room_id: [create_message_schema(msg) for msg in messages] 
        for room_id, messages in groupby([hit['_source'] for hit in search_results['hits']['hits']], key=lambda msg: msg['room_id'])
    }
    return MessagesSearchResultSchema(results=results, total=result_count)


@search_rooms_router.get('/name', response_model=RoomsSearchResultSchema)
async def search_rooms_by_name(n: str, user_uuid: User = Security(get_jwt_user, scopes=ROOM_SCOPES)):
    """
    Search rooms by name, only within rooms the user is a member of.
    :param n: The name to search for
    :param user_uuid: The user's uuid, derived from the JWT token
    :return: `RoomsSearchResultSchema`
    """
    user = User.nodes.get(uuid=user_uuid)
    rooms = user.rooms.filter(room_name__icontains=n)
    results = [RoomSchema.from_orm(room) for room in rooms]
    return RoomsSearchResultSchema(results=results, total=len(results))
