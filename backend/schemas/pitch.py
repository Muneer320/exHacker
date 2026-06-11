from __future__ import annotations

from pydantic import BaseModel


class PitchPackage(BaseModel):
    pitch_30s: str = ""
    pitch_2min: str = ""
    pitch_5min: str = ""
