"""Loopback browser-test app with synthetic provider HTTP boundaries only.

Never run this module for a deployment. Normal app.main has no test switches.
"""

import httpx

from app.core.config import settings
from tests.provider_fixtures import respond

if (
    settings.is_production
    or settings.AI_ACCESS_MODE != "byok"
    or settings.STUDIO_DEMO_MODE
):
    raise RuntimeError("The browser fixture requires development BYOK mode.")

original_client = httpx.AsyncClient


def fixture_client(**kwargs):
    return original_client(transport=httpx.MockTransport(respond), **kwargs)


httpx.AsyncClient = fixture_client

from app.main import app  # noqa: F401
