"""Bound request bodies before JSON parsing, including chunked uploads."""

from starlette.responses import JSONResponse


class RequestBodyLimit:
    def __init__(self, app, max_bytes=200_000):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope["headers"])
        declared = headers.get(b"content-length", b"")
        chunks, size = [], 0
        too_large = declared.isdigit() and int(declared) > self.max_bytes
        while not too_large:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            size += len(chunk)
            if size > self.max_bytes:
                too_large = True
                break
            chunks.append(chunk)
            if not message.get("more_body", False):
                break
        if too_large:
            response = JSONResponse(
                {"success": False, "error": {"message": "Request body is too large."}},
                status_code=413,
                headers={
                    "Cache-Control": "private, no-store",
                    "X-Content-Type-Options": "nosniff",
                },
            )
            return await response(scope, receive, send)
        body = b"".join(chunks)
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        return await self.app(scope, replay, send)
