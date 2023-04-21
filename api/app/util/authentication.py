import logging
import os
from datetime import timedelta, datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.models import User
from app.schemas.jwt import TokenData

JWT_KEY = os.environ['JWT_KEY']
ALGORITHM = 'HS256'
JWT_TOKEN_EXPIRE_MINUTES = os.environ.get('JWT_TOKEN_EXPIRE_MINUTES', 60)

ROOM_SCOPES = [
    # Permissions for rooms
    'get_rooms',
    'search_rooms',
]

MESSAGE_SCOPES = [
    # Permissions for messages
    'get_messages',
    'send_messages',
    'search_messages',
]

USER_SCOPES = ROOM_SCOPES + MESSAGE_SCOPES + ['login', 'logout']  # Permissions for normal users

ADMIN_SCOPES = USER_SCOPES + [
    # Extra permissions for admins on top of normal users
    'admin'
]

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oath2_scheme = OAuth2PasswordBearer(
    tokenUrl='/users/login',
    scopes={
        'get_rooms': 'Get rooms',
        'search_rooms': 'Search rooms',

        'get_messages': 'Get messages',
        'send_messages': 'Send messages',
        'search_messages': 'Search messages',
        
        'login': 'Can login',
        'logout': 'Can logout',
        'admin': 'Is admin',
    }
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a stored hash.
    :param plain_password: The plain password to verify
    :param hashed_password: The stored hash
    :return: True if the password matches the hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> bool | User:
    """
    Authenticate a user by username and password.
    :param username: The username to authenticate
    :param password: The password to authenticate
    :return: The user if the authentication was successful, False otherwise
    """
    user = User.get_user_by_username(username=username)
    if not user:
        logging.error('User %s: user does not exist', username)
        return False
    if not verify_password(password, user.hashed_password):
        logging.error('User %s: password does not match', username)
        return False
    logging.info('User %s: successfully authenticated', username)
    return user


def create_jwt_token(data: dict, expires_delta: int = JWT_TOKEN_EXPIRE_MINUTES) -> str:
    """
    Create a JWT token.
    :param data: The data to encode in the token
    :param expires_delta: The time in minutes until the token expires
    :return: The JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(expires_delta)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, JWT_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_jwt_user(security_scopes: SecurityScopes, token: str = Depends(oath2_scheme)) -> User:
    """
    Get the user from a JWT token. Raises an HTTPException if the token is invalid.
    :param security_scopes: The security scopes the user needs to have
    :param token: The JWT token
    :return: The user
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = 'Bearer'

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': authenticate_value},
    )

    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=[ALGORITHM])
        # check if token is expired
        expires = datetime.fromtimestamp(payload.get('exp'))
        if expires is None or expires < datetime.utcnow():
            raise credentials_exception
        # check if token has user id
        user_uuid: str = payload.get('sub')
        if user_uuid is None:
            raise credentials_exception
        token_scopes = payload.get('scopes', [])
        token_data = TokenData(scopes=token_scopes, user_uuid=user_uuid)
    except (JWTError, ValidationError) as e:
        logging.error('JWT %s: invalid JWT token used with error %s', token, e)
        raise credentials_exception

    # check if user exists
    user = User.get_user_by_id(uuid=user_uuid, lazy=True)
    if user is None:
        raise credentials_exception
    # check if token has valid scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            logging.error('JWT %s: user %s does not have required scope %s', token, user_uuid, scope)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Not enough permissions',
                headers={'WWW-Authenticate': authenticate_value},
            )

    return user_uuid
