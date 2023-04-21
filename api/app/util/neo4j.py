import logging
import os

from neomodel import config as neo4j_config, install_labels, drop_constraints

from app.models import Room, User
from app.models.user import UserStatus, UserStates
from app.util.dummy_data import add_admin_user, add_dummy_users, add_dummy_rooms
from app.util.config import DEBUG


def setup_neo4j():
    # set up ORM connection to Neo4J cluster
    neo4j_config.DATABASE_URL = \
        f"neo4j://{os.environ['NEO4J_USERNAME']}:{os.environ['NEO4J_PASSWORD']}@{os.environ['NEO4J_URI']}:7687"
    logging.info('Neo4j: connecting to Neo4j (%s)...', neo4j_config.DATABASE_URL)
    neo4j_config.AUTO_INSTALL_LABELS = True

    # reset database if we are in development mode
    if DEBUG:
        try:
            logging.info('Neo4j: Dropping constraints...')
            drop_constraints()
            install_labels(UserStatus)
            install_labels(User)
            install_labels(Room)
        except:
            logging.info('Neo4j: No constraints to drop, or some other error')

    # Add default UserStates to db
    for state in UserStates:
        if not UserStatus.nodes.get_or_none(state=state.value):
            UserStatus(state=state.value).save()

    # add admin user if not already present
    add_admin_user()

    # add dummy data (if local development)
    if DEBUG:
        if len(Room.nodes.all(lazy=True)) < 5:
            add_dummy_rooms()
        if len(User.nodes.all(lazy=True)) < 10:
            add_dummy_users()
