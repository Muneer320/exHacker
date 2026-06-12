import logging
from typing import Type, TypeVar, List
from pydantic import BaseModel

from app.core.config import settings
from app.services.llm.providers import (
    BaseLLMProvider,
    GroqProvider,
    GeminiProvider,
    OpenAIProvider,
    OllamaProvider,
)

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMService:
    def __init__(self) -> None:
        self.providers: List[BaseLLMProvider] = []
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initializes all providers in configured priority order."""
        # 1. Groq (Primary, with comma-separated key rotation support)
        groq_keys = settings.groq_api_keys
        if groq_keys:
            logger.info(f"Initializing GroqProvider with {len(groq_keys)} keys.")
            self.providers.append(GroqProvider(groq_keys))
        else:
            logger.warning("GroqProvider API key not configured.")

        # 2. Gemini (Fallback 1)
        if settings.GEMINI_API_KEY:
            logger.info("Initializing GeminiProvider.")
            self.providers.append(GeminiProvider(settings.GEMINI_API_KEY))
        else:
            logger.warning("GeminiProvider API key not configured.")

        # 3. OpenAI (Fallback 2)
        if settings.OPENAI_API_KEY:
            logger.info("Initializing OpenAIProvider.")
            self.providers.append(OpenAIProvider(settings.OPENAI_API_KEY))
        else:
            logger.warning("OpenAIProvider API key not configured.")

        # 4. Ollama (Local Fallback)
        if settings.OLLAMA_HOST:
            logger.info(f"Initializing OllamaProvider at host {settings.OLLAMA_HOST}.")
            self.providers.append(OllamaProvider(settings.OLLAMA_HOST))

    async def generate_with_fallback(
        self, system_prompt: str, user_prompt: str, response_model: Type[T]
    ) -> T:
        """Orchestrates generation, cycling through providers in order of priority."""
        if not self.providers:
            raise RuntimeError(
                "No LLM providers are configured. Please check your environment variables."
            )

        last_exception = None
        for provider in self.providers:
            try:
                logger.info(f"Attempting generation with provider: {provider.name}")
                result = await provider.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_model=response_model,
                )
                logger.info(f"Generation successful with provider: {provider.name}")
                return result
            except Exception as e:
                logger.error(
                    f"Provider {provider.name} failed. Error: {str(e)}. Swapping to fallback."
                )
                last_exception = e

        raise RuntimeError(
            f"All configured LLM providers failed. Last exception: {str(last_exception)}"
        )


# Singleton Instance
llm_service = LLMService()
