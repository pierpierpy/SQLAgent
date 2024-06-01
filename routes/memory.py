from fastapi import APIRouter, Request, HTTPException, status
import models.memory as mr
from typing import Any
from src.auth.auth_bearer import JWTBearer
from src.database.interaction import (
    get_conversation_check,
    clear_memory_by_conversation_id,
    get_conversation_by_user_id_conversation_id,
    get_conversation_id_by_user_id,
)
from fastapi import Depends


router = APIRouter()


@router.delete(
    "/memory/removechatmemory/{conversation_id}",
    response_model=mr.RemoveMemoryOutput,
    tags=["memory"],
    dependencies=[Depends(JWTBearer())],
)
async def clear_memory_route(
    conversation_id: str, user_id: str, request: Request
) -> Any:
    conversation = get_conversation_by_user_id_conversation_id(
        request.app.state.engine, conversation_id=conversation_id, user_id=user_id
    )
    if not conversation:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"conversation_id {conversation_id} not found",
        )
    if not conversation["owned"]:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"conversation_id {conversation_id} not owned by {user_id}",
        )
    clear_memory_by_conversation_id(
        engine=request.app.state.engine,
        conversation_id=conversation_id,
    )
    if conversation_id in request.app.state.conversations:
        request.app.state.conversations.pop(conversation_id)
    return {"conversation_id": conversation_id}


@router.get(
    "/memory/userchat/{conversation_id}",
    response_model=mr.GetChatOutputbyUserID,
    tags=["memory"],
    dependencies=[Depends(JWTBearer())],
)
async def get_conversation_by_user_id_conversation_id_route(
    conversation_id: str, user_id: str, request: Request
) -> Any:

    conversation = get_conversation_by_user_id_conversation_id(
        request.app.state.engine, conversation_id=conversation_id, user_id=user_id
    )
    if not conversation["owned"]:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"conversation_id {conversation_id} not owned by {user_id}",
        )
    return {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "conversation": conversation["convs"],
        "len_memory": len(conversation["convs"]),
    }


@router.get(
    "/memory/userconversations/",
    response_model=mr.GetConvIdsOutputbyUserID,
    tags=["memory"],
    dependencies=[Depends(JWTBearer())],
)
async def get_conversation_ids_by_user_id_route(user_id: str, request: Request) -> Any:
    # TODO check if user exists and has conversations
    conversation_ids = get_conversation_id_by_user_id(
        request.app.state.engine, user_id=user_id
    )

    return {
        "conversation_ids": conversation_ids,
        "user_id": user_id,
    }


############# OLD ROUTES #############
# @router.get(
#     "/memory/chatmemory/{conversation_id}",
#     response_model=mr.GetMemoryOutput,
#     tags=["memory"],
#     dependencies=[Depends(JWTBearer())],
# )
# async def get_memory(conversation_id: str, request: Request) -> Any:
#     if not get_conversation_check(
#         engine=request.app.state.engine, conversation_id=conversation_id
#     ):
#         raise HTTPException(
#             status.HTTP_404_NOT_FOUND, f"conversation id {conversation_id} not found"
#         )
#     agent = request.app.state.conversations[conversation_id]
#     memory = agent.memory.chat_memory.messages
#     return {
#         "conversation_id": conversation_id,
#         "memory": memory,
#         "len_memory": len(memory),
#     }
