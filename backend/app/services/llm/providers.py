import json
import logging
from abc import ABC, abstractmethod
from typing import Type, TypeVar, List, Optional
import httpx
from pydantic import BaseModel, ValidationError

# Clients
from groq import AsyncGroq
import google.generativeai as genai
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str, response_model: Type[T]) -> T:
        """Asynchronously generate structured output from the LLM."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class GroqProvider(BaseLLMProvider):
    def __init__(self, api_keys: List[str]) -> None:
        self.api_keys = api_keys
        self.current_key_index = 0
        self.clients = [AsyncGroq(api_key=key) for key in api_keys] if api_keys else []

    @property
    def name(self) -> str:
        return "groq"

    def _get_client(self) -> Optional[AsyncGroq]:
        if not self.clients:
            return None
        return self.clients[self.current_key_index]

    def _rotate_key(self) -> None:
        if len(self.clients) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.clients)
            logger.info(f"Rotating to Groq API key index {self.current_key_index}")

    async def generate(self, system_prompt: str, user_prompt: str, response_model: Type[T]) -> T:
        if not self.clients:
            raise ValueError("No Groq API keys available")

        max_key_retries = len(self.clients)
        last_exception = None

        for attempt in range(max_key_retries):
            client = self._get_client()
            if not client:
                raise ValueError("No active Groq client found")

            try:
                # Use standard model for quick structured tasks
                model_name = "llama3-70b-8192"
                
                # In Groq, JSON mode is activated by setting response_format to {"type": "json_object"}
                # and instructions to return JSON in prompt.
                chat_completion = await client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": f"{system_prompt}\nReturn valid JSON only. Matching the schema: {response_model.model_json_schema()}"},
                        {"role": "user", "content": user_prompt},
                    ],
                    model=model_name,
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
                
                content = chat_completion.choices[0].message.content
                if not content:
                    raise ValueError("Groq returned an empty response")
                
                parsed_data = json.loads(content)
                return response_model.model_validate(parsed_data)

            except Exception as e:
                logger.warning(f"Groq API call failed with key index {self.current_key_index}: {str(e)}")
                last_exception = e
                # Check for rate limit or similar API errors to trigger key rotation
                self._rotate_key()

        raise last_exception or RuntimeError("All Groq keys failed during generation")


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)

    @property
    def name(self) -> str:
        return "gemini"

    async def generate(self, system_prompt: str, user_prompt: str, response_model: Type[T]) -> T:
        if not self.api_key:
            raise ValueError("Gemini API key not configured")

        # Select model based on typical usage
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # We specify the system instruction, user prompt, and generation config for JSON Schema output
        generation_config = {
            "response_mime_type": "application/json",
            "response_schema": response_model,
            "temperature": 0.2
        }

        # google-generativeai client generation
        response = await model.generate_content_async(
            contents=[
                {"role": "user", "parts": [user_prompt]}
            ],
            generation_config=generation_config,
            # Pass system instruction through system_instruction param
            system_instruction=system_prompt
        )

        content = response.text
        if not content:
            raise ValueError("Gemini returned an empty response")

        parsed_data = json.loads(content)
        return response_model.model_validate(parsed_data)


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None

    @property
    def name(self) -> str:
        return "openai"

    async def generate(self, system_prompt: str, user_prompt: str, response_model: Type[T]) -> T:
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        chat_completion = await self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=response_model,
            temperature=0.2,
        )

        result = chat_completion.choices[0].message.parsed
        if not result:
            raise ValueError("OpenAI failed to parse response into model")
        return result


class OllamaProvider(BaseLLMProvider):
    def __init__(self, host: str) -> None:
        self.host = host

    @property
    def name(self) -> str:
        return "ollama"

    async def generate(self, system_prompt: str, user_prompt: str, response_model: Type[T]) -> T:
        # Use http client directly for Ollama endpoint to remain dependency-light
        url = f"{self.host}/api/chat"
        
        payload = {
            "model": "llama3",
            "messages": [
                {"role": "system", "content": f"{system_prompt}\nReturn JSON matching the schema: {response_model.model_json_schema()}"},
                {"role": "user", "content": user_prompt}
            ],
            "format": "json",
            "options": {
                "temperature": 0.2
            },
            "stream": False
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"Ollama returned status code {response.status_code}: {response.text}")

            result = response.json()
            content = result.get("message", {}).get("content", "")
            if not content:
                raise ValueError("Ollama returned an empty response")

            parsed_data = json.loads(content)
            return response_model.model_validate(parsed_data)
