from datetime import timedelta, datetime
import jwt

from asgiref.sync import sync_to_async
from ninja.router import Router
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import User
from ..core.db_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


SECRET_KEY = SECRET_KEY
ALGORITHM = ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES

auth_router = Router()


@auth_router.post("register/")
async def register(request, data: dict):
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return {'error': "It's necessary to fill username, password and email fields."}

    if await sync_to_async(User.objects.filter)(username=username).exists():
        return {'error': 'This username is already taken.'}

    user = await sync_to_async(User.objects.create)(
        username=username,
        password=make_password(password),
        email=email
    )

    return {'success': f'User {user.username} successfully registered.'}


@auth_router.post("login/")
async def login(request, data: dict):
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {'error': "It's necessary to fill username, password and email fields."}

    user = authenticate(username=username, password=password)

    if not user:
        return {'error': 'Wrong username or password.'}

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )

    return {'access_token': access_token, 'token_type': 'bearer'}


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
