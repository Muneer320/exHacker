"""Single-process, owner-bound credential leases. Nothing in this module is serialized."""

import asyncio
import contextlib
import secrets
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from pydantic import SecretStr

from app.studio.errors import CredentialsRequiredError, StudioError


@dataclass(repr=False)
class Lease:
    owner: str
    provider: str
    model: str
    secret: SecretStr
    deadline: float
    expires_at: str
    calls: set[asyncio.Task] = field(default_factory=set)


class LeaseRegistry:
    """Accessed exclusively on the API/worker event loop; never across processes."""

    def __init__(self, clock=time.monotonic, ttl=1800, capacity=512):
        self.clock = clock
        self.ttl = ttl
        self.capacity = capacity
        self._entries: dict[str, Lease] = {}

    def _drop(self, handle):
        entry = self._entries.pop(handle, None)
        if entry:
            entry.secret = SecretStr("")
            for task in tuple(entry.calls):
                task.cancel()
            entry.calls.clear()

    def cleanup(self):
        for handle, entry in tuple(self._entries.items()):
            if entry.deadline <= self.clock():
                self._drop(handle)

    def clear(self):
        for handle in tuple(self._entries):
            self._drop(handle)

    def create(self, owner, provider, model, secret: SecretStr):
        self.cleanup()
        if (
            len(self._entries) >= self.capacity
            or sum(e.owner == owner for e in self._entries.values()) >= 3
        ):
            raise StudioError(
                "AI session limit reached. Remove an old session first.", 429
            )
        handle = secrets.token_urlsafe(32)
        self._entries[handle] = Lease(owner, provider, model, secret, 0, "")
        self.renew(owner, handle)
        return self.metadata(owner, handle)

    def get(self, owner, handle):
        self.cleanup()
        entry = self._entries.get(handle)
        if not entry or not secrets.compare_digest(entry.owner, owner):
            raise CredentialsRequiredError()
        return entry

    def metadata(self, owner, handle):
        entry = self.get(owner, handle)
        return {
            "id": handle,
            "provider": entry.provider,
            "model": entry.model,
            "expires_at": entry.expires_at,
        }

    def renew(self, owner, handle):
        # A new lease starts at zero; expired existing leases cannot be revived.
        entry = self._entries.get(handle)
        if not entry or not secrets.compare_digest(entry.owner, owner):
            raise CredentialsRequiredError()
        if entry.deadline and entry.deadline <= self.clock():
            self._drop(handle)
            raise CredentialsRequiredError()
        entry.deadline = self.clock() + self.ttl
        entry.expires_at = (datetime.now(UTC) + timedelta(seconds=self.ttl)).isoformat()

    def revoke(self, owner, handle):
        self.get(owner, handle)
        self._drop(handle)

    def revoke_all(self, owner):
        for handle, entry in tuple(self._entries.items()):
            if secrets.compare_digest(entry.owner, owner):
                self._drop(handle)

    def contains_secret(self, text):
        self.cleanup()
        return any(e.secret.get_secret_value() in text for e in self._entries.values())

    async def run(self, owner, handle, call):
        entry = self.get(owner, handle)
        task = asyncio.create_task(call(entry.secret.get_secret_value()))
        entry.calls.add(task)
        try:
            while not task.done():
                await asyncio.wait(
                    {task}, timeout=max(0.001, entry.deadline - self.clock())
                )
                self.get(owner, handle)
            result = await task
            self.get(owner, handle)
            return result
        except asyncio.CancelledError:
            if asyncio.current_task().cancelling():
                raise
            raise CredentialsRequiredError() from None
        finally:
            if not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task
            entry.calls.discard(task)


leases = LeaseRegistry()


async def cleanup_loop():
    while True:
        leases.cleanup()
        await asyncio.sleep(1)
