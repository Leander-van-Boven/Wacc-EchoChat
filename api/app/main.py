import logging
import os

from fastapi import FastAPI
import sentry_sdk
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from app.routers import generic_router, messages_router, rooms_router, room_id_router
from app.routers.admin import admin_websocket_endpoint
from app.routers.user import users_router
from app.routers.search import search_messages_router, search_rooms_router
from app.routers.websocket import websocket_endpoint, websocket_manager
from app.util import setup_cassandra, setup_neo4j
from app.util.elasticsearch import es as elasticsearch_client, setup_elasticsearch
from app.util.config import APP_NAME, DEBUG, TESTING


logging.basicConfig(
    level=2,
    format='%(asctime)-15s %(levelname)-8s %(name)s %(message)s',
)


if not TESTING and not DEBUG:
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        traces_sample_rate=0,  # We use Tempo for tracing
    )

# Create the FastAPI app
app = FastAPI(title='Echochat API', root_path=os.environ.get("ROOT_PATH", ""))

# Add middlewares
app.add_middleware(CORSMiddleware,
                   allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

if not TESTING and not DEBUG:
    from app.util.monitoring import PrometheusMiddleware, metrics, setting_otlp
    
    app.add_middleware(PrometheusMiddleware, app_name=APP_NAME)
    app.add_route('/metrics', metrics)
    setting_otlp(app, APP_NAME, f'http://{os.environ.get("GRPC_TEMPO_OTLP_URI", "localhost")}:{os.environ.get("GRPC_TEMPO_OTLP_PORT", "4317")}')

    class EndpointFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.getMessage().find('GET /metrics') == -1

    logging.getLogger('uvicorn.access').addFilter(EndpointFilter())


# Add routers to the app
app.include_router(generic_router)
app.include_router(users_router)
app.include_router(rooms_router)
app.include_router(room_id_router)
app.include_router(messages_router)
app.include_router(search_messages_router)
app.include_router(search_rooms_router)
app.add_api_websocket_route('/ws/{conn_id}', websocket_endpoint)
app.add_api_websocket_route('/ws/admin/{conn_id}', admin_websocket_endpoint)


@app.on_event('startup')
async def startup() -> None:
    if TESTING:
        logging.info('App: skipping startup tasks for testing')
    else:
        try:
            setup_neo4j()
            setup_cassandra()
            await setup_elasticsearch()
            await websocket_manager.startup()
        except Exception as e:
            logging.error(f'App: startup tasks failed: {e}')


@app.on_event('shutdown')
async def shutdown() -> None:
    try:
        await websocket_manager.shutdown()
    except:
        logging.info('App: failed to shutdown websocket_manager, or it was already shutdown')
        pass

    try:
        await elasticsearch_client.close()
    except:
        logging.info('App: failed to close elasticsearch connection, or it was already closed')
        pass


if __name__ == '__main__':
    log_config = uvicorn.config.LOGGING_CONFIG
    if not DEBUG and not TESTING:
        log_config["formatters"]["access"]["fmt"] = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s] - %(message)s"
    uvicorn.run(
        '__main__:app', 
        host='0.0.0.0', 
        port=int(os.environ.get('PORT', '80')), 
        log_config=log_config,
        log_level= 'info',
        reload=DEBUG,
        proxy_headers=True,
    )
