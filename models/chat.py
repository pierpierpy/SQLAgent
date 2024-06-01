from pydantic import BaseModel, Field
from typing import Any


###################### ###################### ###################### STALE MODELS ###################### ###################### ###################### ######################
# from langchain.agents.agent import AgentExecutor
# from typing import List

# TODO[] use this class for the list of agents
# class Agents(BaseModel):
#     id: str
#     agent: AgentExecutor


# class ChatOutput(BaseModel):
#     answer: str = Field(...)

#     class Config:
#         json_schema_extra = {"example": {"answer": "this is the answer"}}

###################### ###################### ###################### ###################### ###################### ###################### ######################


class ChatInput(BaseModel):
    query: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "count the number of each category in the Settore column",
            }
        }


# TODO[] queste vanno in un file apparte memory nei models
class GetConversationOutput(BaseModel):
    conversation_id: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "xxxxxxx",
            }
        }
