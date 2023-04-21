from uuid import UUID

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


class Message(Model):
    """
    A message in a room, stored in Cassandra.

    Reasoning behind the order of the columns, and primary keys:
    - Most performed queries:
        - Get messages in a room, ordered by date: `room_id` and `index_id`
        - Get a single message by id
            - to update stats like distributed, saved, etc: `uuid`
            - to perform actions like delete, reply, etc: `uuid`
        - create new messages, which could be a reply to another message: `uuid`

    - Other queries:
        - Get messages by sender: `sender_id`

    For all queries containing the `uuid`, we know the `room_id``,
    `room_id` has been chosen as the primary partition key.
    Sadly, because we need to be able to retrieve messages on `room_id` only,
    we cannot utilize the high cardinality of `uuid` as a composite partition key.

    We could've used TimeUUID for `uuid` and `index_id` combined as it both encodes a unique identifier in combination
    with a timestamp, however, from a security perspective, it is not recommended to use TimeUUIDs as the use UUID1.
    Hence, we use UUID4 for `uuid` and `index_id` is a DateTime.

    We use an index on `sender_id` to allow us to query for all messages by a sender in all rooms,
    while also being able to query for all messages by a sender in a room.

    Optionally we might add indexes on `saved`, `distributed`, `seen`, `deleted`, `failure`
    to allow us to query for all messages with a certain state. Though, since these values will change over time,
    it is not recommended to use indexes on these columns.
    """

    room_id: UUID = columns.UUID(primary_key=True, partition_key=True)
    index_id = columns.DateTime(primary_key=True, clustering_order='ASC')
    uuid: UUID = columns.UUID(primary_key=True)
    sender_id: UUID = columns.UUID(required=True, index=True)

    content: str = columns.Text(required=True)

    username: str = columns.Text(required=False)
    avatar: str = 'https://avatars.githubusercontent.com/u/16872793?v=4'

    message_date = columns.Date(db_field='date')
    message_stamp = columns.Time(db_field='stamp')

    # system = columns.Boolean(default=False)  # to show message in the middle of the chat

    # TODO: dynamically update below methods
    saved: bool = columns.Boolean(default=True)
    distributed: bool = columns.Boolean(default=False)
    seen: bool = columns.Boolean(default=False)
    deleted: bool = columns.Boolean(default=False)
    failure: bool = columns.Boolean(default=False)

    # Hardcoded values, might be changed in the future
    disable_actions = False
    disable_reactions = False

    reply_message: UUID | None = columns.UUID(required=False, default=None)

    # Disabled fields, since we don't need them for MVP
    files = []
    reactions = []

    @property
    def date(self):
        return self.message_date.date()

    @property
    def time_stamp(self):
        return self.message_stamp.time()
