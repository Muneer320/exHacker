import io
import zipfile
from pathlib import Path
from typing import Any

import structlog

from app.artifacts.architecture_generator import ArchitectureGenerator
from app.artifacts.pitch_generator import PitchGenerator
from app.artifacts.prd_generator import PRDGenerator
from app.artifacts.readme_generator import ReadmeGenerator
from app.schemas.state import ExHackerState

logger = structlog.get_logger()


class ExportService:

    def __init__(self) -> None:
        self.logger = logger.bind(service="export")
        self.generators = {
            "readme": ReadmeGenerator(),
            "prd": PRDGenerator(),
            "architecture": ArchitectureGenerator(),
            "pitch": PitchGenerator(),
        }

    async def generate_all(self, state: ExHackerState | dict[str, Any], output_dir: Path) -> dict[str, Path]:
        state_dict = self._to_dict(state)
        results: dict[str, Path] = {}
        for name, gen in self.generators.items():
            try:
                path = await gen.save(state_dict, output_dir)
                results[name] = path
                self.logger.info("artifact_generated", name=name, path=str(path))
            except Exception:
                self.logger.exception("artifact_generation_failed", name=name)
                raise
        return results

    async def generate_zip(self, state: ExHackerState | dict[str, Any]) -> bytes:
        state_dict = self._to_dict(state)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, gen in self.generators.items():
                try:
                    markdown = await gen.generate(state_dict)
                    zf.writestr(gen.filename, markdown.encode("utf-8"))
                    self.logger.info("artifact_added_to_zip", name=name, filename=gen.filename)
                except Exception:
                    self.logger.exception("artifact_zip_failed", name=name)
                    raise
        return buf.getvalue()

    def _to_dict(self, state: ExHackerState | dict[str, Any]) -> dict[str, Any]:
        if isinstance(state, ExHackerState):
            return state.model_dump()
        return state
