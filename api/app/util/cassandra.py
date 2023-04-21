import logging
import os

from cassandra.cluster import Cluster, DCAwareRoundRobinPolicy
from cassandra.cqlengine import connection as cassandra_connection
from cassandra.cqlengine.management import sync_table

from app.models import Message
from app.util.dummy_data import add_dummy_messages
from app.util.config import DEBUG, TESTING

CASSANDRA_URI = os.environ.get('CASSANDRA_URI', 'localhost:9042')
CASSANDRA_DEFAULT_KEYSPACE = os.environ['CASSANDRA_DEFAULT_KEYSPACE'] \
    if not TESTING else 'test'

get_messages_pstmt = None


def setup_cassandra():
    """
    Sets up the Cassandra connection, and makes sure the keyspace and Message table exist.
    """
    # connect to Cassandra cluster
    cluster = Cluster(
        [os.environ['CASSANDRA_URI']], 
        load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='DC1'),
        protocol_version=4
    )
    session = cluster.connect()

    # TODO: disabled because it interferes with the elasticsearch sync
    # if os.environ.get('DEBUG', False):
    #     session.execute(f"""
    #         DROP KEYSPACE IF EXISTS
    #         {os.environ['CASSANDRA_DEFAULT_KEYSPACE']}
    #     """)

    # create keyspace if it doesn't exist
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS 
        {CASSANDRA_DEFAULT_KEYSPACE} 
        WITH REPLICATION = {{'class': 'NetworkTopologyStrategy', 'DC1': '3'}}
    """)

    # setup ORM connection
    cassandra_connection.setup(
        [CASSANDRA_URI],
        CASSANDRA_DEFAULT_KEYSPACE,
        load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='DC1'),
        protocol_version=4
    )
    logging.info('Connecting to Cassandra (%s)...', CASSANDRA_URI)

    # apply ORM model to database
    sync_table(Message)

    # add dummy data (if local development)
    if DEBUG:
        if Message.objects.count() == 0:
            add_dummy_messages()
