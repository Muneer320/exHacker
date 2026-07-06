"""Prompt Manager — loads, renders, and validates prompts from YAML files.

Prompts are data, not code. They live in YAML files, version-controlled.
Rendering is deterministic (string.Template). No AI is used to build prompts.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)

PROMPTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "prompts",
)


class PromptTemplate:
    """A loaded prompt template with system instruction and user template."""

    def __init__(
        self,
        name: str,
        version: int = 1,
        model_tier: int = 2,
        system: str = "",
        user: str = "",
        fallback: Optional[str] = None,
    ) -> None:
        self.name = name
        self.version = version
        self.model_tier = model_tier
        self.system = system
        self.user_template = user
        self.fallback = fallback

    def render(self, **variables: Any) -> tuple[str, str]:
        """Render the prompt by substituting variables into the user template."""
        if not self.user_template:
            return self.system, ""
        try:
            user_prompt = self.user_template.format(**variables)
        except KeyError as e:
            logger.warning("Missing variable %s in prompt '%s'", e, self.name)
            user_prompt = self.user_template
        return self.system, user_prompt


class PromptManager:
    """Loads and manages prompt templates from YAML files."""

    def __init__(self, prompts_dir: str = PROMPTS_DIR) -> None:
        self._prompts_dir = prompts_dir
        self._cache: dict[str, PromptTemplate] = {}

    def load(self, name: str) -> PromptTemplate:
        """Load a prompt template by name."""
        cache_key = name
        if cache_key in self._cache:
            return self._cache[cache_key]

        filepath = os.path.join(self._prompts_dir, f"{name}.yaml")
        if not os.path.exists(filepath):
            available = self.list_prompts()
            raise FileNotFoundError(
                f"Prompt '{name}' not found at {filepath}. Available: {available}"
            )

        with open(filepath) as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid prompt file: {filepath}")

        prompt = PromptTemplate(
            name=data.get("name", name),
            version=data.get("version", 1),
            model_tier=data.get("model_tier", 2),
            system=data.get("system", ""),
            user=data.get("user", ""),
            fallback=data.get("fallback"),
        )
        self._cache[cache_key] = prompt
        return prompt

    def render(self, name: str, **variables: Any) -> tuple[str, str]:
        """Load and render a prompt in one step."""
        prompt = self.load(name)
        return prompt.render(**variables)

    def list_prompts(self) -> list[str]:
        """List all available prompt names."""
        if not os.path.exists(self._prompts_dir):
            return []
        files = os.listdir(self._prompts_dir)
        return sorted(f.replace(".yaml", "") for f in files if f.endswith(".yaml"))


prompt_manager = PromptManager()
