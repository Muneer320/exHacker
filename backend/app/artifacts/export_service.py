from __future__ import annotations

import io
import json
import zipfile
from typing import Any

from app.artifacts.architecture_generator import ArchitectureGenerator
from app.artifacts.base import ArtifactGenerator
from app.artifacts.implementation_guide_generator import ImplementationGuideGenerator
from app.artifacts.prd_generator import PRDGenerator
from app.artifacts.readme_generator import ReadmeGenerator


class ExportService:
    def __init__(self) -> None:
        self._generators: list[ArtifactGenerator] = [
            ReadmeGenerator(),
            ArchitectureGenerator(),
            PRDGenerator(),
            ImplementationGuideGenerator(),
        ]

    def generate_all(self, state: dict[str, Any]) -> dict[str, str]:
        artifacts: dict[str, str] = {}
        for gen in self._generators:
            try:
                artifacts[gen.name] = gen.generate(state)
            except Exception:
                artifacts[gen.name] = f"# {gen.name}\n\nFailed to generate artifact."
        return artifacts

    def generate_zip(self, state: dict[str, Any]) -> bytes:
        artifacts = self.generate_all(state)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, content in artifacts.items():
                zf.writestr(f"{name}.md", content)
            zf.writestr("state_snapshot.json", json.dumps(state, indent=2, default=str))
        buffer.seek(0)
        return buffer.getvalue()
