from langchain_community.document_loaders.text import TextLoader
from langchain_community.vectorstores import faiss
from langchain_openai import AzureOpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_core.vectorstores import VectorStoreRetriever
from src.openai.custom_prompts import TOOL_PROMPT_RAG


def init_index(embeddings: AzureOpenAIEmbeddings):
    # TODO migliorare il parsing
    loader = TextLoader(
        "./src/dataAugmentation/glossario_rag.txt", autodetect_encoding=True
    )
    documents = loader.load()
    texts = documents[0].page_content.split("###")
    index = faiss.FAISS.from_texts(texts, embeddings)
    return index


# TODO JACOPO usa questo per inizializzare il tool di retrival
def init_rag_tool(retriever: VectorStoreRetriever):
    tool = create_retriever_tool(
        retriever.as_retriever(),
        name="SearchDocument",
        description=TOOL_PROMPT_RAG,
    )
    return tool
