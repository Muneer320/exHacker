from typing import Any

import structlog
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings

logger = structlog.get_logger()


class LLMService:
    def __init__(self) -> None:
        self._model: ChatOpenAI | None = None

    def _get_model(self) -> ChatOpenAI:
        if self._model is None:
            api_key: str | None = settings.openai_api_key or None
            self._model = ChatOpenAI(
                model=settings.openai_model,
                temperature=settings.openai_temperature,
                api_key=api_key,  # type: ignore[arg-type]
            )
        return self._model

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        messages: list[BaseMessage] = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        model = self._get_model()
        response = await model.ainvoke(messages)
        return str(response.content)

    async def generate_structured(
        self, system_prompt: str, user_prompt: str, response_format: type
    ) -> Any:
        messages: list[BaseMessage] = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        model = self._get_model().with_structured_output(response_format)
        return await model.ainvoke(messages)


llm_service = LLMService()
