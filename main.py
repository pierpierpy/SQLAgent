from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from sqlalchemy.exc import OperationalError
from fastapi import HTTPException, status
from src.database.interaction import get_conversations_as_dicts
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router as chat_routes
from routes.auth import router as auth_routes
from routes.memory import router as memory_routes
from src.dataAugmentation.init import init_index
from src.openai.init import init_super_agent
from src.openai.utils import init_sql_agent
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

import uvicorn

parent_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(parent_dir, ".env")
load_dotenv(env_path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """lifespan event instead of on_event_startup (deprecated)"""

    db_connection_string = os.environ.get("db_connection_string") + os.environ.get(
        "db_name"
    )
    try:
        engine = create_engine(db_connection_string)
    except OperationalError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="connection to db failed"
        )
    llm = AzureChatOpenAI(
        azure_deployment=os.environ.get("CHAT_MODEL_NAME"),
        azure_endpoint=os.environ.get("CHAT_OPENAI_API_BASE"),
        openai_api_key=os.environ.get("CHAT_OPENAI_API_KEY"),
        openai_api_version=os.environ.get("CHAT_OPENAI_API_VERSION"),
        temperature=0,
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )
    emb = AzureOpenAIEmbeddings(
        azure_deployment=os.environ.get("EMB_MODEL_NAME"),
        azure_endpoint=os.environ.get("EMB_OPENAI_API_BASE"),
        openai_api_key=os.environ.get("EMB_OPENAI_API_KEY"),
        openai_api_version=os.environ.get("EMB_OPENAI_API_VERSION"),
    )
    index = init_index(emb)
    app.state.retriever = index
    app.state.llm = llm
    app.state.engine = engine
    app.state.emb = emb
    # TODO[] re-inizializzare gli agent insieme agli id
    app.state.conversation_ids = get_conversations_as_dicts(engine)
    if app.state.conversation_ids.values():
        app.state.conversations = {
            conversation_id: init_super_agent(
                llm,
                conversation_id,
                index,
                init_sql_agent(
                    llm,
                    engine,
                    conversation_id,
                ),
                engine=engine,
            )
            for conversation_id in app.state.conversation_ids
        }
    else:
        app.state.conversations = app.state.conversation_ids
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(chat_routes)
app.include_router(auth_routes)
app.include_router(memory_routes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# TODO scommentare questo quando mandiamo in prod
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
