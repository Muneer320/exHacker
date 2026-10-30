"""No networks or real credentials: test the RAM lifecycle directly."""

import asyncio

import pytest
from pydantic import SecretStr

from app.studio.credentials import LeaseRegistry
from app.studio.errors import CredentialsRequiredError, StudioError


def test_isolation_expiration_renewal_and_cleanup():
    clock = [10.0]
    registry = LeaseRegistry(clock=lambda: clock[0], ttl=30)
    metadata = registry.create("alice", "openai", "model", SecretStr("fixture-secret"))
    handle = metadata["id"]
    entry = registry.get("alice", handle)
    assert "fixture-secret" not in repr(entry)
    assert "fixture-secret" not in str(metadata)
    with pytest.raises(CredentialsRequiredError):
        registry.get("bob", handle)
    clock[0] += 20
    registry.renew("alice", handle)
    clock[0] += 20
    assert registry.get("alice", handle) is entry
    clock[0] += 11
    registry.cleanup()
    assert entry.secret.get_secret_value() == ""
    assert registry._entries == {}
    with pytest.raises(CredentialsRequiredError):
        registry.renew("alice", handle)


def test_capacity_revoke_and_restart():
    registry = LeaseRegistry(capacity=4)
    for _ in range(3):
        registry.create("alice", "groq", "model", SecretStr("fixture-secret"))
    with pytest.raises(StudioError, match="limit"):
        registry.create("alice", "groq", "model", SecretStr("fixture-secret"))
    bob = registry.create("bob", "groq", "model", SecretStr("bob-secret"))
    registry.revoke_all("alice")
    assert len(registry._entries) == 1
    registry.revoke("bob", bob["id"])
    assert not registry._entries
    lease = registry.create("alice", "groq", "model", SecretStr("fixture-secret"))
    registry.clear()
    with pytest.raises(CredentialsRequiredError):
        registry.get("alice", lease["id"])


@pytest.mark.parametrize("action", ["revoke", "expire", "shutdown"])
async def test_active_requests_close_on_revoke_expiry_or_shutdown(action):
    registry = LeaseRegistry(ttl=0.025 if action == "expire" else 30)
    metadata = registry.create("alice", "openai", "model", SecretStr("fixture-secret"))
    started, closed = asyncio.Event(), asyncio.Event()

    async def request(key):
        assert key == "fixture-secret"
        try:
            started.set()
            await asyncio.Future()
        finally:
            closed.set()

    task = asyncio.create_task(registry.run("alice", metadata["id"], request))
    await started.wait()
    if action == "revoke":
        registry.revoke("alice", metadata["id"])
    elif action == "shutdown":
        registry.clear()
    with pytest.raises(CredentialsRequiredError):
        await task
    assert closed.is_set()
    assert not registry._entries
