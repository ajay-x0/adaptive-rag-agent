# Architecture Notes

## Runtime flow

The application has three layers:

1. **Presentation** — Streamlit chat and document upload.
2. **API** — FastAPI endpoints that accept queries and documents.
3. **Agentic RAG workflow** — LangGraph manages routing, retrieval, grading, rewriting and generation.

## Query routing

The classifier receives the latest user question and retrieved context and returns one of:

- `index`
- `general`
- `search`

The routing decision is then converted into a LangGraph transition.

## Retrieval feedback loop

The indexed-document path is intentionally not:

`query → retrieve → generate`

Instead:

`query → retrieve → grade → generate`

or:

`query → retrieve → grade → rewrite → retrieve → ...`

This creates a feedback loop for retrieval quality.

## Data stores

### FAISS

Uploaded document chunks are embedded with OpenAI embeddings and persisted under `storage/faiss/`.

### MongoDB

Conversation messages are persisted using an asynchronous MongoDB-backed chat history implementation. The session ID is used as the conversation key.

## External services

- OpenAI: generation + embeddings
- Tavily: external search
- MongoDB: conversation persistence

API keys and connection strings are loaded through environment variables.
