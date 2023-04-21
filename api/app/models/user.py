from typing import Dict
from uuid import UUID

from neomodel import UniqueIdProperty, StructuredNode, StringProperty, RelationshipTo, RelationshipFrom, \
    DateTimeProperty, BooleanProperty, StructuredRel

from app.models import UserStates, RoomRel


class StatusRel(StructuredRel):
    """
    Relationship class between User and Status to keep track of the last time the status was changed.
    """
    last_changed = DateTimeProperty(default_now=True, format='%Y-%m-%d %H:%M:%S')


# noinspection PyAbstractClass
class UserStatus(StructuredNode):
    """
    Node class for the status of a user.
    Only two states are allowed: 'online' and 'offline'.

    The status of a user is also represented as a node in a graph database since we can then easily change the
    connection of a user node to its respective status node, thereby allowing us to do an insanely fast lookup of
    all users with a specific status, as it's just a matter of finding all connected nodes to a status node.
    """
    USER_STATES = {status.value: status.value for status in UserStates}

    state = StringProperty(choices=USER_STATES, default=UserStates.OFFLINE.value)
    users = RelationshipFrom('User', 'HAS_STATUS', model=StatusRel)

    @classmethod
    def get_online_status(cls) -> 'UserStatus':
        return cls.nodes.get_or_none(state=UserStates.ONLINE.value)

    @classmethod
    def get_offline_status(cls) -> 'UserStatus':
        return cls.nodes.get_or_none(state=UserStates.OFFLINE.value)


# noinspection PyAbstractClass
class User(StructuredNode):
    """
    Representation of a user as a node in a graph database. This representation was chosen in combination with the
    node representation of a room, since it allows us to easily find all users in a room, and all rooms a user is in.

    Furthermore, the resulting social graph offers a lot of possibilities for further development.
    """
    uuid = UniqueIdProperty()
    username = StringProperty(required=True, unique_index=True)
    hashed_password = StringProperty(required=True)
    is_admin = BooleanProperty(default=False)
    avatar = 'https://avatars.githubusercontent.com/u/33727726?s=40&v=4'
    status_rel = RelationshipTo(UserStatus, 'HAS_STATUS', model=StatusRel)
    rooms = RelationshipTo('.room.Room', 'IN_ROOM', model=RoomRel)

    def get_status(self) -> Dict[str, str]:
        """
        Custom property to get the current status of the user, since the status of a user consists of the UserStatus
        node the User is connected to, as well as the last time the status was changed (contained in the relation).
        :return: `dict`
        """
        current_status = self.status_rel.single()
        if current_status and current_status.state:
            return {
                'state': current_status.state,
                'last_changed': self.status_rel.relationship(current_status).last_changed,
            }
        return {
            'state': UserStates.OFFLINE.value,
            'last_changed': '',
        }

    @classmethod
    def get_user_by_username(cls, username: str, **kwargs) -> 'User':
        return cls.nodes.get_or_none(username=username, **kwargs)

    @classmethod
    def get_user_by_id(cls, uuid: UUID | str, **kwargs) -> 'User':
        return cls.nodes.get_or_none(uuid=uuid, **kwargs)
