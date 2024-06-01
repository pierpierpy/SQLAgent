from langchain_core.messages import BaseMessage
from typing import List
from langchain_community.chat_message_histories.sql import (
    SQLChatMessageHistory,
    BaseMessageConverter,
    DefaultMessageConverter,
)
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.tools import Tool
from pydantic.v1 import BaseModel, Field
from src.openai.custom_prompts import TOOL_PROMPT_SQL_AGENT
from langchain_openai.chat_models import AzureChatOpenAI

from langchain.memory import ConversationBufferWindowMemory
from sqlalchemy import Engine
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.agents import create_openai_tools_agent
from langchain.agents.agent import AgentExecutor
import os
from langchain_community.agent_toolkits.sql.prompt import (
    SQL_FUNCTIONS_SUFFIX,
)
from src.openai.custom_prompts import (
    CUSTOM_SQL_SYSTEM_PROMPT,
)
from sqlalchemy.orm import sessionmaker
from typing import Any, List, Optional
from langchain_core.messages import (
    BaseMessage,
)


class KSQLChatMessageHistory(SQLChatMessageHistory):
    def __init__(
        self,
        session_id: str,
        connection_string: str = None,
        engine: Engine = None,
        k: int = 6,
        table_name: str = "message_store",
        session_id_field_name: str = "session_id",
        custom_message_converter: Optional[BaseMessageConverter] = None,
        *args,
        **kwargs
    ):
        if connection_string is not None:
            super().__init__(
                session_id,
                connection_string,
                table_name,
                session_id_field_name,
                custom_message_converter,
                *args,
                **kwargs
            )
        else:
            if engine is None:
                raise ValueError("An engine or connection_string must be provided")
            self.engine = engine
            self.session_id_field_name = session_id_field_name
            self.converter = custom_message_converter or DefaultMessageConverter(
                table_name
            )
            self.sql_model_class = self.converter.get_sql_model_class()
            if not hasattr(self.sql_model_class, session_id_field_name):
                raise ValueError("SQL model class must have a session_id column")
            self.session_id = session_id
            self.Session = sessionmaker(bind=self.engine)
        self.k = k

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve all messages from db"""
        with self.Session() as session:
            result = (
                session.query(self.sql_model_class)
                .where(
                    getattr(self.sql_model_class, self.session_id_field_name)
                    == self.session_id
                )
                .order_by(self.sql_model_class.id.asc())
            )
            messages = []
            for record in result:
                messages.append(self.converter.from_sql_model(record))
            return messages[-self.k * 2 :]


class EngineSQLDatabase(SQLDatabase):
    @classmethod
    def from_engine(cls, engine: Engine) -> SQLDatabase:
        """Construct a SQLAlchemy engine"""
        return cls(engine)


class SQLAgentInput(BaseModel):
    sql_input: str = Field(description="user query")


def init_sql_agent_tool(sql_agent: AgentExecutor) -> Tool:

    sql_agent_tool = Tool.from_function(
        name="SQLAGENT",
        description=TOOL_PROMPT_SQL_AGENT,
        func=lambda sql_input: sql_agent.invoke({"sql_input": sql_input}),
        args_schema=SQLAgentInput,
        # return_direct=True,  # TODO questo qui purtroppo pare essere un bug di langchain
    )
    return sql_agent_tool


def init_sql_agent(
    llm: AzureChatOpenAI, engine: Engine, session_id: str
) -> AgentExecutor:
    db = EngineSQLDatabase.from_engine(engine)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    context = toolkit.get_context()
    tools = toolkit.get_tools()

    memory_history = KSQLChatMessageHistory(
        session_id=session_id,
        engine=engine,
        k=int(os.environ.get("K_MEMORY_SQL_AGENT")),
        table_name="message_store_sql_agent",
    )
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        input_key="sql_input",
        output_key="output",
        chat_memory=memory_history,
        return_messages=True,
    )
    messages = [
        SystemMessage(content=CUSTOM_SQL_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
        HumanMessagePromptTemplate.from_template(
            "ANSWER TO THIS QUESTION: {sql_input}"
        ),
        AIMessage(content=SQL_FUNCTIONS_SUFFIX),
    ]
    prompt = ChatPromptTemplate.from_messages(messages)

    prompt = prompt.partial(**context)

    sql_agent = create_openai_tools_agent(llm, tools, prompt)

    sql_agent_executor = AgentExecutor(
        name="SQLAGENT",
        agent=sql_agent,
        tools=tools,
        verbose=True,
        memory=memory,
    )
    return sql_agent_executor
