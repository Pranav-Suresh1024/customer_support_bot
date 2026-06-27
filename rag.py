import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import KNOWLEDGE_DIR
from utils import setup_logger
from state import AgentState

logger = setup_logger(__name__)

# Global vector store instance
_vector_store = None

def initialize_rag():
    """Initializes the FAISS vector store with documents from KNOWLEDGE_DIR."""
    global _vector_store
    
    docs = []
    for filename in ["company_policy.txt", "pricing_guide.txt", "technical_manual.txt", "faq.txt"]:
        file_path = os.path.join(KNOWLEDGE_DIR, filename)
        if os.path.exists(file_path):
            loader = TextLoader(file_path)
            docs.extend(loader.load())
        else:
            logger.warning(f"Knowledge file not found: {file_path}")
            
    if not docs:
        logger.warning("No knowledge documents loaded. RAG will not return any context.")
        return
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    splits = text_splitter.split_documents(docs)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    _vector_store = FAISS.from_documents(splits, embeddings)
    logger.info(f"Initialized RAG vector store with {len(splits)} chunks.")

def rag_retrieval_node(state: AgentState) -> AgentState:
    """
    Retrieves top-k relevant chunks and adds them to state.
    Skips retrieval entirely for Memory intent queries.
    """
    # Memory queries use SQLite history, not the knowledge base
    if state.get("intent") == "Memory":
        state["retrieved_context"] = ""
        state["retrieved_chunks"] = []
        logger.info("RAG skipped: Memory intent query.")
        return state

    global _vector_store
    if _vector_store is None:
        initialize_rag()

    query = state["user_query"]

    if _vector_store is None:
        logger.warning("Vector store unavailable. Check knowledge files.")
        state["retrieved_context"] = ""
        state["retrieved_chunks"] = []
        return state

    retriever = _vector_store.as_retriever(search_kwargs={"k": 3})
    results = retriever.invoke(query)

    chunks = []
    for doc in results:
        source = os.path.basename(doc.metadata.get("source", "unknown"))
        chunks.append(f"[Source: {source}]\n{doc.page_content}")

    state["retrieved_context"] = "\n\n".join(chunks)
    state["retrieved_chunks"] = chunks
    logger.info(f"RAG retrieved {len(chunks)} chunks.")
    return state
