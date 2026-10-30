"""Credentials have a dedicated, nonpersistent endpoint and response schema."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from app.core.config import settings
from app.studio.auth import owner_key
from app.studio.credentials import leases
from app.studio.errors import StudioError
from app.studio.providers import model_spec

router = APIRouter(prefix="/ai/leases")


class CredentialInput(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    provider: str = Field(max_length=30)
    model: str = Field(max_length=100)
    key: SecretStr = Field(min_length=8, max_length=512)


@router.post("", status_code=201)
async def create_lease(payload: CredentialInput, owner=Depends(owner_key)):
    if settings.STUDIO_DEMO_MODE or settings.AI_ACCESS_MODE != "byok":
        raise StudioError("User API sessions are disabled in this server mode.", 409)
    model_spec(payload.provider, payload.model)
    key = payload.key.get_secret_value()
    if not key.isascii() or any(c.isspace() or ord(c) < 33 for c in key):
        raise StudioError(
            "Enter a valid API key without spaces or control characters.", 422
        )
    key = ""
    return {
        "success": True,
        "data": leases.create(owner, payload.provider, payload.model, payload.key),
    }


@router.delete("")
async def revoke_all(owner=Depends(owner_key)):
    leases.revoke_all(owner)
    return {"success": True, "data": None}


@router.get("/{handle}")
async def lease_status(handle: str, owner=Depends(owner_key)):
    return {"success": True, "data": leases.metadata(owner, handle)}


@router.post("/{handle}/renew")
async def renew_lease(handle: str, owner=Depends(owner_key)):
    leases.renew(owner, handle)
    return {"success": True, "data": leases.metadata(owner, handle)}


@router.delete("/{handle}")
async def revoke_lease(handle: str, owner=Depends(owner_key)):
    leases.revoke(owner, handle)
    return {"success": True, "data": None}
