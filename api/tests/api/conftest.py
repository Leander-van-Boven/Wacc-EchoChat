from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest

from fastapi.testclient import TestClient

from app.models import User
from app.models.enums import UserStates
from app.schemas.user import UserSchema, UserStateSchema


@pytest.fixture
def app():
    from app.main import app
    return app


@pytest.fixture
def client(app):
    client = TestClient(app)
    return client


@pytest.fixture
def user_status():
    return UserStates.OFFLINE.value


@pytest.fixture
def test_user():
    return {
        'username': 'test',
        'password': 'test',
    }


@pytest.fixture
def user_exists():
    return True


@pytest.fixture
def mock_get_user_by_username(user_exists):
    with patch('app.routers.user.User.get_user_by_username') as mock:
        def side_effect(username):
            if user_exists:
                return User(uuid=uuid4(), username=username)
            return None

        mock.side_effect = side_effect
        yield mock


@pytest.fixture
def mock_get_user_by_id(user_exists):
    with patch('app.routers.user.User.get_user_by_id') as mock:
        def side_effect(user_id):
            if user_exists:
                return User(uuid=user_id, username='test')
            return None

        mock.side_effect = side_effect
        yield mock


@pytest.fixture
def mock_user_save():
    with patch('app.routers.user.User.save') as mock:
        yield mock


@pytest.fixture
def mock_user_status_rel():
    with patch('app.routers.user.UserSchema.from_orm') as mock:
        def side_effect(user):
            return UserSchema(
                uuid=user.uuid,
                username=user.username,
                is_admin=user.is_admin,
                avatar=user.avatar,
                status=UserStateSchema(
                    state=UserStates.OFFLINE.value,
                    last_changed=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                ),
            )

        mock.side_effect = side_effect
        yield mock
