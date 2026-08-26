"""OpenAI chat model initialization."""

from langchain_openai import ChatOpenAI

from src.core.config import settings

llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    api_key=settings.OPENAI_API_KEY,
)
