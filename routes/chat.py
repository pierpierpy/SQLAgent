from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import StreamingResponse
import models.chat as mc
from typing import Any
from fastapi import Depends
from src.auth.auth_bearer import JWTBearer
import random
from src.openai.init import init_super_agent
from src.openai.utils import init_sql_agent
from src.database.interaction import (
    get_conversation_check,
    create_user_conversation_ownership,
    update_number_of_messages_owner_conversation,
)
import string
import re
from fastapi.encoders import jsonable_encoder
import json

router = APIRouter()


# TODO[] if no conversation id is passed, throw error
@router.post(
    "/chat/qa/{conversation_id}",
    tags=["chat"],
    # response_model=mc.ChatOutput, # TODO verificare un modello corretto per l'output di una route che fa streaming?
    dependencies=[Depends(JWTBearer())],
)
async def chat(chatinput: mc.ChatInput, conversation_id, request: Request) -> Any:
    """chat route, calls the agent and executes the query"""

    # TODO[] when conversation is created the id should be inserted in the table
    if not (
        get_conversation_check(
            engine=request.app.state.engine, conversation_id=conversation_id
        )
        or (conversation_id in request.app.state.conversations)
    ):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"conversation id {conversation_id} not found"
        )
    agent = request.app.state.conversations[conversation_id]

    async def response_stream(query):
        async for response in agent.astream_log({"input_superagent": query}):
            if response.ops[0]["path"] == "/logs/AzureChatOpenAI/final_output":
                if (
                    "tool_calls"
                    in response.ops[0]["value"]["generations"][0][0][
                        "message"
                    ].additional_kwargs
                ):
                    yield json.dumps(
                        {
                            "meta": response.ops[0]["value"]["generations"][0][0][
                                "message"
                            ].additional_kwargs["tool_calls"][0]["function"]["name"]
                        }
                    ) + "\n"

            if re.fullmatch(
                r"/logs/AzureChatOpenAI(:\d+)?/streamed_output_str/-",
                response.ops[0]["path"],
            ):
                yield json.dumps({"ans": response.ops[0]["value"]}) + "\n"

    update_number_of_messages_owner_conversation(
        request.app.state.engine, conversation_id=conversation_id
    )
    return StreamingResponse(
        response_stream(chatinput.query), media_type="text/event-stream"
    )


@router.get(
    "/chat/conversation",
    response_model=mc.GetConversationOutput,
    tags=["chat"],
    dependencies=[Depends(JWTBearer())],
)
async def get_conversation(user_id: str, request: Request) -> Any:
    letters = string.ascii_lowercase
    length = 15
    conversation_id = "".join(random.choice(letters) for _ in range(length))

    super_agent = init_super_agent(
        llm=request.app.state.llm,
        session_id=conversation_id,
        retriever=request.app.state.retriever,
        sql_agent=init_sql_agent(
            llm=request.app.state.llm,
            engine=request.app.state.engine,
            session_id=conversation_id,
        ),
        engine=request.app.state.engine,
    )
    create_user_conversation_ownership(
        request.app.state.engine, conversation_id=conversation_id, user_id=user_id
    )
    request.app.state.conversations[conversation_id] = super_agent
    return {"conversation_id": conversation_id}
