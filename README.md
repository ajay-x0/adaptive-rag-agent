# Adaptive RAG Agent

> An agentic Retrieval-Augmented Generation system that dynamically chooses between document retrieval, general LLM reasoning, and web search.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-orange)
![FAISS](https://img.shields.io/badge/Vector%20Store-FAISS-purple)
![MongoDB](https://img.shields.io/badge/Memory-MongoDB-brightgreen)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

## Overview

Traditional RAG pipelines retrieve documents for every query. This project adds an orchestration layer that first analyzes the query and selects an appropriate execution path:

1. **Indexed documents** — retrieve context from uploaded PDF/TXT files.
2. **General knowledge** — answer directly with the LLM when retrieval is unnecessary.
3. **Web search** — use Tavily when the question requires external or current information.

For document questions, retrieved context is graded for relevance. If the context is insufficient, the query is rewritten and retrieval is attempted again before generation.

The application exposes the pipeline through a FastAPI backend and provides a Streamlit interface for document upload and chat.

## Architecture

```text
                         ┌───────────────────┐
                         │   Streamlit UI    │
                         │  Chat + Upload    │
                         └─────────┬─────────┘
                                   │ HTTP
                                   ▼
                         ┌───────────────────┐
                         │    FastAPI API    │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │    LangGraph      │
                         │   Query Analysis  │
                         └─────────┬─────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
       ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
       │ Document RAG│      │ General LLM │      │ Web Search  │
       └──────┬──────┘      └─────────────┘      └──────┬──────┘
              │                                          │
              ▼                                          │
       ┌─────────────┐                                   │
       │ Relevance   │                                   │
       │   Grader    │                                   │
       └──────┬──────┘                                   │
          yes │ no                                        │
              │  └──────────► Query Rewrite ──► Retrieve │
              │                                          │
              └──────────────────┬───────────────────────┘
                                 ▼
                         ┌───────────────────┐
                         │ Answer Generation │
                         └─────────┬─────────┘
                                   ▼
                              Final Answer
```

## LangGraph workflow

| Node | Responsibility |
|---|---|
| `query_analysis` | Classifies the query as indexed-document, general, or search |
| `retriever` | Uses a ReAct agent and document retriever to obtain relevant context |
| `grade` | Checks whether retrieved context is relevant |
| `rewrite` | Rewrites unsuccessful retrieval queries |
| `web_search` | Retrieves external context with Tavily |
| `general_llm` | Handles general-purpose questions |
| `generate` | Produces the final user-facing response |

## Tech Stack

- **Python** — application and orchestration code
- **LangGraph** — stateful workflow orchestration
- **LangChain** — LLM, retrieval and tool abstractions
- **OpenAI** — chat model and embeddings
- **FAISS** — local vector similarity search
- **FastAPI** — REST API
- **MongoDB / Motor** — persistent conversation history
- **Tavily** — external web search
- **Streamlit** — interactive UI
- **Pydantic** — request and structured-output models

## Project Structure

```text
adaptive-rag-agent/
├── src/
│   ├── api/              # FastAPI routes
│   ├── config/            # Prompt configuration
│   ├── core/              # Runtime settings
│   ├── db/                # MongoDB client
│   ├── llms/              # LLM integration
│   ├── memory/            # Conversation history
│   ├── models/            # Pydantic / graph state models
│   ├── rag/               # Graph, retrieval and document ingestion
│   └── tools/             # Routing and helper tools
├── streamlit_app/         # Web UI
├── docs/                  # Architecture notes
├── storage/faiss/         # Local generated vector index (ignored by Git)
├── .env.example
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB
- OpenAI API key
- Tavily API key for the web-search route

### Installation

```bash
git clone https://github.com/ajay-x0/adaptive-rag-agent.git
cd adaptive-rag-agent

python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

### Environment

```bash
cp .env.example .env
```

Fill in `OPENAI_API_KEY` and `TAVILY_API_KEY`.

### Start the API

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

### Start Streamlit

In another terminal:

```bash
streamlit run streamlit_app/home.py
```

> The current UI contains an authentication integration pointing at a separate service on port `8080`. The Python RAG backend itself exposes the query and document-upload endpoints. If that external authentication service is not available, use the FastAPI endpoints directly or adapt the UI authentication layer.

## API

### Query

```http
POST /rag/query
Content-Type: application/json
```

```json
{
  "query": "What does the uploaded document say about X?",
  "session_id": "demo-session"
}
```

### Document upload

```http
POST /rag/documents/upload
X-Description: A document about X
Content-Type: multipart/form-data
```

Supported formats:

- PDF
- TXT

## Example flow

**Query:** `What technologies are mentioned in my uploaded resume?`

→ Query classifier detects relevant indexed context

→ FAISS retrieves document chunks

→ Relevance grader evaluates the context

→ Generator produces a grounded response

For a query such as:

**Query:** `What is the weather in Pune today?`

→ Indexed context is not sufficient

→ Router selects web search

→ Tavily provides external context

→ Generator produces the answer

For a general question:

**Query:** `What is a REST API?`

→ Router selects the general LLM path

→ No unnecessary document retrieval is performed.

## Design Decisions

### Why LangGraph?

The workflow contains conditional transitions rather than a single linear chain. LangGraph makes those states and transitions explicit and allows the application to retry retrieval after query rewriting.

### Why relevance grading?

Retrieving a document does not guarantee that it answers the query. A grading step gives the workflow a feedback signal and prevents immediately generating an answer from obviously irrelevant context.

### Why query rewriting?

Poor retrieval can result from vocabulary mismatch between the user's question and the indexed document. Rewriting gives the retriever a second, more targeted query.

### Why FAISS?

The current implementation uses FAISS as a lightweight local vector store. The code keeps vector-store access behind the retriever layer, making a future migration to a managed vector database possible without redesigning the entire graph.

## Limitations

This is a portfolio / learning implementation rather than a production deployment.

Current limitations include:

- FAISS is local to the application instance.
- Document metadata and multi-user document isolation need further hardening.
- The Streamlit authentication flow depends on a separate service not included in this repository.
- Evaluation metrics and automated RAG benchmarks are not yet included.
- Web-search and LLM calls require external API credentials.

## Future Improvements

- Add automated RAG evaluation with faithfulness, relevance and answer-quality metrics.
- Introduce document-level and user-level access control.
- Add a managed vector database option such as Qdrant.
- Add Docker Compose for API, UI, MongoDB and vector infrastructure.
- Add unit/integration tests for graph routing and retrieval.
- Add observability and latency/token-cost tracking.
- Add streaming responses.
- Add CI with linting, tests and security checks.

## Reference & Attribution

This project was developed with reference to the open-source
[`dhruvsinghal09/Adaptive-Rag`](https://github.com/dhruvsinghal09/Adaptive-Rag)
project, particularly its Adaptive RAG workflow concepts and overall application architecture.

The reference repository's README states that it is licensed under the MIT License. This repository is not affiliated with or endorsed by the original author. See `THIRD_PARTY_NOTICES.md` for attribution context.

## License

MIT License. See `LICENSE`.
