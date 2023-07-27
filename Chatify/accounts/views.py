from datetime import timedelta, datetime
import jwt

from asgiref.sync import sync_to_async
from ninja.router import Router
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from core.db_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

from .schemas import UserRegisterIn, UserLoginIn

SECRET_KEY = SECRET_KEY
ALGORITHM = ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES

auth_router = Router()


@auth_router.post("register/")
async def register(request, data: UserRegisterIn):
    email = data.email
    phone_number = data.phone_number
    username = data.username
    password = data.password

    if not username or not password or not email or not phone_number:
        return {'error': "It's necessary to fill username, password, email and phone number fields."}

    if await sync_to_async(CustomUser.objects.filter(username=username).exists)():
        return {'error': 'This username is already taken.'}

    if await sync_to_async(CustomUser.objects.filter(phone_number=phone_number).exists)():
        return {'error': 'An account with this phone number is already exists.'}

    if await sync_to_async(CustomUser.objects.filter(email=email).exists)():
        return {'error': 'An account with this email is already exists.'}

    user = await sync_to_async(CustomUser.objects.create)(
        email=email,
        phone_number=phone_number,
        username=username,
        password=make_password(password),
    )

    return {'success': f'User {user.username} successfully registered.'}


@auth_router.post("login/")
async def login(request, data: UserLoginIn):
    username = data.username
    password = data.password

    if not username or not password:
        return {'error': "It's necessary to fill username, password and email fields."}

    user = await sync_to_async(authenticate)(username=username, password=password)

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
