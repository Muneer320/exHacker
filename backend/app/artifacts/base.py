from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


class ArtifactGenerator(ABC):

    name: str = "artifact"
    filename: str = "artifact.md"

    def __init__(self) -> None:
        self.logger = logger.bind(generator=self.name)

    @abstractmethod
    async def generate(self, state: dict[str, Any]) -> str:
        ...

    async def save(self, state: dict[str, Any], output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        markdown = await self.generate(state)
        file_path = output_dir / self.filename
        file_path.write_text(markdown, encoding="utf-8")
        self.logger.info("artifact_saved", path=str(file_path), size=len(markdown))
        return file_path
