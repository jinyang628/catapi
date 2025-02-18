from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    role: Role
    content: str


class MessagePayload(BaseModel):
    thread_id: Optional[str]
    message: Message
