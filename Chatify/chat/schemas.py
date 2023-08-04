from pydantic import BaseModel


class MessageIn(BaseModel):
    text: str
