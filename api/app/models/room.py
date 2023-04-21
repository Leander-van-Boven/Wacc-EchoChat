from typing import Generator, TYPE_CHECKING

from neomodel import StringProperty, IntegerProperty, DateTimeProperty, UniqueIdProperty, \
    StructuredNode, StructuredRel, BooleanProperty, RelationshipFrom

from app.schemas.user import UserSchema

if TYPE_CHECKING:
    from app.models.user import User


class RoomRel(StructuredRel):
    is_typing = BooleanProperty(default=False)  # TODO: revise this


# noinspection PyAbstractClass
class Room(StructuredNode):
    """
    Representation of a chatroom, as a node in a graph database.
    This node representation compared to other database representations seems to be the most efficient for the use case,
    as users are also represented as nodes, and the relationship between users and rooms is a many-to-many relationship,
    best displayed using edges in a graph database.

    Furthermore, this allows us to, in the future, perform social graph analysis on the data, such as finding the most
    popular rooms, or the most popular users.
    """

    uuid = UniqueIdProperty()
    room_name = StringProperty(default=f'Room_{uuid}')
    unread_count = IntegerProperty(default=0)
    index = DateTimeProperty(default_now=True, format='%Y-%m-%d %H:%M:%S')
    last_message = StringProperty(default=None)  # TODO: check if this needs to be a uuid or needs to be a full Message
    connected_users = RelationshipFrom('.user.User', 'IN_ROOM', model=RoomRel)

    @property
    def users(self) -> Generator[UserSchema, None, None]:
        """
        Return generator for obtaining all users in this room as UserSchema objects.
        """
        return (UserSchema.from_orm(user) for user in self.connected_users.all())

    @property
    def typing_users(self) -> Generator['User', None, None]:
        return (
            user
            for user
            in self.connected_users.all()
            if self.connected_users.relationship(user).is_typing
        )
