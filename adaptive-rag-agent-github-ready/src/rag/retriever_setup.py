"""Document embedding and FAISS retriever setup."""

import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.tools import create_retriever_tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from src.core.config import settings

embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
_vectorstore = None


def _index_path() -> Path:
    path = Path(settings.FAISS_INDEX_PATH)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load_vectorstore():
    global _vectorstore

    index_dir = _index_path()
    if (index_dir / "index.faiss").exists() and (index_dir / "index.pkl").exists():
        _vectorstore = FAISS.load_local(
            str(index_dir),
            embeddings,
            allow_dangerous_deserialization=True,
        )
    return _vectorstore


def retriever_chain(chunks: list[Document]) -> bool:
    """Add document chunks to the local FAISS index and persist it."""
    global _vectorstore

    try:
        if _vectorstore is None:
            _vectorstore = _load_vectorstore()

        if _vectorstore is None:
            _vectorstore = FAISS.from_documents(chunks, embeddings)
        else:
            _vectorstore.add_documents(chunks)

        _vectorstore.save_local(str(_index_path()))
        return True
    except Exception as exc:
        print(f"Error storing documents in FAISS: {exc}")
        return False


def get_retriever():
    """Return a LangChain retriever tool over the indexed documents."""
    global _vectorstore

    if _vectorstore is None:
        _vectorstore = _load_vectorstore()

    if _vectorstore is None:
        dummy = Document(
            page_content="No documents have been uploaded yet. Ask the user to upload a document.",
            metadata={"source": "initialization"},
        )
        _vectorstore = FAISS.from_documents([dummy], embeddings)

    description_path = Path("description.txt")
    description = description_path.read_text(encoding="utf-8") if description_path.exists() else "the uploaded documents"

    return create_retriever_tool(
        _vectorstore.as_retriever(),
        "retriever_uploaded_documents",
        f"Use this tool only for questions about: {description}",
    )
