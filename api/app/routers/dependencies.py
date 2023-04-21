import logging

from fastapi import HTTPException

from app.util.cassandra import setup_cassandra, cassandra_connection


async def ensure_cassandra_connection() -> bool:
    """
    Checks if the Cassandra connection is established, and if not, tries to establish it.
    """
    try:
        cassandra_connection.get_connection()
        return True
    except Exception as e:
        try:
            setup_cassandra()
            return True
        except Exception as e:
            logging.error('Error while connecting to Cassandra: %s', e)
            raise HTTPException(status_code=500, detail='Error while connecting to Cassandra') from e
