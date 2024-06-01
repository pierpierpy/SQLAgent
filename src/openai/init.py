from src.openai.custom_prompts import (
    SUPERAGENT_SYSTEM_PROMPT,
)
from langchain_openai.chat_models import AzureChatOpenAI

from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.agents import create_openai_tools_agent
from langchain.agents.agent import AgentExecutor
from src.openai.utils import KSQLChatMessageHistory
from src.dataAugmentation.init import init_rag_tool
from langchain_core.vectorstores import VectorStoreRetriever
from src.openai.utils import init_sql_agent_tool
import os
from sqlalchemy import Engine


def init_super_agent(
    llm: AzureChatOpenAI,
    session_id: str,
    retriever: VectorStoreRetriever,
    sql_agent: AgentExecutor,
    engine: Engine,
) -> AgentExecutor:

    tools = [init_rag_tool(retriever), init_sql_agent_tool(sql_agent)]

    # TODO qui bisogna mettere l'engine, non la connection strin, vedi sql.py

    memory_history = KSQLChatMessageHistory(
        session_id=session_id,
        engine=engine,
        k=int(os.environ.get("K_MEMORY_SUPER_AGENT")),
        table_name="message_store_super_agent",
    )

    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        input_key="input_superagent",
        output_key="output",
        chat_memory=memory_history,
        return_messages=True,
    )
    messages = [
        SystemMessage(content=SUPERAGENT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
        HumanMessagePromptTemplate.from_template(
            "ANSWER TO THIS QUESTION: {input_superagent}"
        ),
    ]
    prompt = ChatPromptTemplate.from_messages(messages)

    super_agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        name="SUPERAGENT",
        agent=super_agent,
        tools=tools,
        memory=memory,
        max_execution_time=300,
        early_stopping_method="force",
    )
    return agent_executor
