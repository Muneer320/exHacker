"""Anonymous workspace capability authentication."""

import hashlib
import re

from fastapi import Header

from app.studio.errors import StudioError


def owner_key(authorization: str = Header(default="")):
    match = re.fullmatch(r"Bearer ([0-9a-f]{64})", authorization)
    if not match:
        raise StudioError(
            "A workspace access key is required. Open exHacker in your browser to create one.",
            401,
        )
    return hashlib.sha256(match[1].encode()).hexdigest()
