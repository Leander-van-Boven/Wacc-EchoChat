import logging
import os
from typing import Any, Mapping, Optional, Union, Collection, Tuple

from elasticsearch import AsyncElasticsearch 
from elastic_transport import AsyncTransport
from elastic_transport._models import DEFAULT, DefaultType
from elastic_transport._transport import TransportApiResponse

from app.util.config import TESTING

message_index = os.environ['CASSANDRA_DEFAULT_KEYSPACE'] if not TESTING else 'test'


class NoCompatibleWithHeaderTransport(AsyncTransport):
    """Ugly hack to make elasticsearch 8.x work with Elassandra 6.x"""
    async def perform_request(
        self,
        method: str,
        target: str,
        *,
        body: Optional[Any] = None,
        headers: Union[Mapping[str, Any], DefaultType] = DEFAULT,
        max_retries: Union[int, DefaultType] = DEFAULT,
        retry_on_status: Union[Collection[int], DefaultType] = DEFAULT,
        retry_on_timeout: Union[bool, DefaultType] = DEFAULT,
        request_timeout: Union[Optional[float], DefaultType] = DEFAULT,
        client_meta: Union[Tuple[Tuple[str, str], ...], DefaultType] = DEFAULT,
    ) -> TransportApiResponse:
        if 'Content-Type' in headers:
            headers['Content-Type'] = 'application/json'

        meta, resp_body = await super().perform_request(
            method,
            target,
            body=body,
            headers=headers,
            max_retries=max_retries,
            retry_on_status=retry_on_status,
            retry_on_timeout=retry_on_timeout,
            request_timeout=request_timeout,
            client_meta=client_meta,
        )

        if not meta.headers.get("x-elastic-product", None):
            meta.headers["x-elastic-product"] = "Elasticsearch"
        
        return meta, resp_body


if TESTING:
    es = None
else:
    es = AsyncElasticsearch(f'http://{os.environ["ELASTICSEARCH_URI"]}:{os.environ["ELASTICSEARCH_PORT"]}',
                            transport_class=NoCompatibleWithHeaderTransport)
    logging.info('Elasticsearch: connection established...')


async def setup_elasticsearch():
    logging.info('Elasticsearch: setting up Elasticsearch indices from Cassandra schema...')
    if not await es.indices.exists(index=message_index):
        await es.indices.create(
            index=message_index, 
            mappings={
                "message": {
                    "discover": "^((?!content).)*$",
                    "properties": {
                        "content": {
                            "type": "text",
                            "cql_collection": "singleton",
                        },
                    }
                }
            }
        )
