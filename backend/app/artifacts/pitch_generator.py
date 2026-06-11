from __future__ import annotations

from typing import Any

from app.artifacts.base import ArtifactGenerator


class PitchGenerator(ArtifactGenerator):
    @property
    def name(self) -> str:
        return "pitch"

    def generate(self, state: dict[str, Any]) -> str:
        pitch = state.get("pitch", {}) or {}

        if isinstance(pitch, dict):
            return f"""# Pitch Package

## 30 Second Pitch

{pitch.get('pitch_30s', '')}

## 2 Minute Pitch

{pitch.get('pitch_2m', '')}

## 5 Minute Pitch

{pitch.get('pitch_5m', '')}

## Demo Script

{pitch.get('demo_script', '')}
"""
        return "# Pitch Package\n\nPitch information not available."
