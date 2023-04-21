import asyncio
import logging
import os
from uuid import UUID

from starlette.websockets import WebSocket

from app.models.user import User, UserStatus


async def send_user_statistics(websocket: WebSocket):
    online_status = UserStatus.get_online_status()
    online_user_count = len(online_status.users)
    await websocket.send_json({
        'type': 'user_statistics',
        'data': {
            'action': 'user_statistics_update',
            'statistics': {
                'userCount': len(User.nodes.all()),
                'onlineUsers': online_user_count,
            }
        }
    })


async def handle_admin_websocket(websocket: WebSocket):
    while True:
        try:
            await send_user_statistics(websocket)
            await asyncio.sleep(os.environ.get('ADMIN_WEBSOCKET_INTERVAL', 10))
        except Exception as e:
            logging.error('Admin: Error while sending user statistics %s', e)
            break


async def admin_websocket_endpoint(ws: WebSocket, conn_id: str) -> None:
    user = User.get_user_by_id(uuid=UUID(conn_id).hex)
    if user is None or not user.is_admin:
        logging.warning('Admin: User %s tried to connect to admin websocket', conn_id)
        await ws.close()
        return

    await ws.accept()
    await asyncio.create_task(handle_admin_websocket(ws))
