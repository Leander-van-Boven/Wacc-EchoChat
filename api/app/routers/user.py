from datetime import datetime
import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Security

from app.models import User, UserStatus
from app.schemas.jwt import JWTToken, LoginSchema
from app.schemas.user import UserSchema
from app.util.authentication import ADMIN_SCOPES, authenticate_user, create_jwt_token, USER_SCOPES, get_jwt_user, \
    get_password_hash

users_router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={
        401: {'description': 'Incorrect username or password'},
        403: {'description': 'User is not authorized to access this resource'},
        409: {'description': 'User already exists'}
    }
)

user_id_router = APIRouter(
    prefix='/users/{user_id}',
    tags=['users'],
    responses={
        401: {'description': 'Could not validate credentials'},
        403: {'description': 'Incorrect username or password'},
        404: {'description': 'User Not found'},
    },
    dependencies=[Security(get_jwt_user, scopes=ADMIN_SCOPES)]
)


@users_router.post('', status_code=201, response_model=UserSchema)
async def create_user(login_data: LoginSchema):
    """
    Create a new user, based on the login data provided.
    :param login_data: A combination of username and password
    :return: The newly created user as a `UserSchema`
    """
    username = login_data.username

    # Check if user already exists
    if User.get_user_by_username(username=username):
        raise HTTPException(status_code=409, detail='User already exists')

    # Create user
    user = User(username=username, hashed_password=get_password_hash(login_data.password))
    user.save()

    logging.info('User %s: created', user.uuid)
    return UserSchema.from_orm(user)


@users_router.post('/login', response_model=JWTToken)
async def login_user(login_data: LoginSchema):
    """
    Login a user, based on the login data provided.
    :param login_data: A combination of username and password
    :return: A JWT token for the user (consisting of the actual token, a type, user_uuid and whether it is an admin JWT)
    """
    user = authenticate_user(login_data.username, login_data.password)

    if not user:
        raise HTTPException(status_code=401, detail='Incorrect username or password')
    elif user.is_admin:
        raise HTTPException(status_code=401, detail='Admins cannot login to chat')

    # create token
    token = create_jwt_token(data={'sub': user.uuid, 'scopes': USER_SCOPES})

    # Set user status to online
    online_status = UserStatus.get_online_status()
    user.status_rel.replace(online_status)
    user.status_rel.last_changed = datetime.utcnow()

    logging.info('User %s: logged in', user.uuid)
    return JWTToken(token=token, token_type='bearer', user_uuid=user.uuid)


@users_router.post('/login/admin', response_model=JWTToken)
async def login_admin(login_data: LoginSchema):
    """
    Login an admin, based on the login data provided.
    :param login_data: A combination of username and password
    :return: A JWT token for the admin user, JWT will have `is_admin` set to `True`.
    """
    user = authenticate_user(login_data.username, login_data.password)

    if not user:
        raise HTTPException(status_code=401, detail='Incorrect username or password')
    if not user.is_admin:
        raise HTTPException(status_code=403, detail='User is not an admin')

    token = create_jwt_token(data={'sub': user.uuid, 'scopes': ADMIN_SCOPES})

    logging.info('Admin %s: logged in', user.uuid)
    return JWTToken(token=token, token_type='bearer', user_uuid=user.uuid, is_admin=True)


@users_router.post('/logout', status_code=204)
async def logout_user(user_uuid: UUID = Security(get_jwt_user, scopes=USER_SCOPES)):
    """
    Logout a user. User to logout is determined by the JWT token.
    :param user_uuid: The UUID of the user to logout, derived from the JWT token.
    :return: 204 status code
    """
    user = User.get_user_by_id(uuid=user_uuid)
    offline_status = UserStatus.get_offline_status()
    user.status_rel.replace(offline_status)
    user.status_rel.last_changed = datetime.utcnow()

    logging.info('User %s: logged out', user.uuid)
    return None


@user_id_router.get('', response_model=UserSchema)
async def get_user(user_id: UUID):
    """
    Get a user by their UUID.
    :param user_id: The UUID of the user to get
    :return: `UserSchema`
    """
    user = User.get_user_by_id(uuid=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return UserSchema.from_orm(user)
