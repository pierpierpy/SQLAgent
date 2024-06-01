from pydantic import BaseModel, Field
from typing import Any


class GetMemoryOutput(BaseModel):
    conversation_id: str
    memory: Any  # TODO[] fix this typing with the correct one
    len_memory: int

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "xxxxxxx",
            }
        }


class RemoveMemoryOutput(BaseModel):
    conversation_id: str

    class Config:
        json_schema_extra = {"example": {"conversation_id": "xxxxxxx"}}


class GetChatOutputbyUserID(BaseModel):
    conversation_id: str
    user_id: str
    conversation: Any
    len_memory: int

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "xxxxxxx",
                "user_id": "xxx",
                "conversation": [],
                "len_memory": 3,
            }
        }


class GetConvIdsOutputbyUserID(BaseModel):
    conversation_ids: list
    user_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": ["xxxxxxx"],
                "user_id": "xxx",
            }
        }
