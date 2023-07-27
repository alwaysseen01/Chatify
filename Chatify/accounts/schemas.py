from pydantic import BaseModel


class UserRegisterIn(BaseModel):
    email: str
    phone_number: str
    username: str
    password: str


class UserLoginIn(BaseModel):
    username: str
    password: str
