import logging
import os

from distributed_websocket import WebSocketManager
from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from app.util.config import TESTING

REDIS_HOST = os.environ.get('REDIS_URI', 'redis://localhost')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_CONNECTION_URI = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0'

redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    socket_connect_timeout=1
)


async def check_redis_connection():
    try:
        await redis_client.ping()
        return True
    except ConnectionError as e:
        logging.error('Redis: connection failed')
        return False


def setup_websocket_manager():
    if TESTING:
        return WebSocketManager('channel:1', broker_url='memory://')
    return WebSocketManager(
        'echochat:messages',
        REDIS_CONNECTION_URI
    )
