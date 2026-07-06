"""Custom exceptions for exHacker.

Every failure has a predictable path.
Users see friendly messages. Engineers get full context.
"""

from typing import Any


class ExHackerError(Exception):
    """Base exception for all exHacker errors."""

    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."
    status_code: int = 500
    detail: dict[str, Any] | None = None
    suggestion: str | None = None

    def __init__(
        self,
        message: str | None = None,
        detail: dict[str, Any] | None = None,
        suggestion: str | None = None,
    ) -> None:
        if message:
            self.message = message
        if detail:
            self.detail = detail
        if suggestion:
            self.suggestion = suggestion
        super().__init__(self.message)


class ProjectNotFoundError(ExHackerError):
    code = "PROJECT_NOT_FOUND"
    message = "Project not found."
    status_code = 404
    suggestion = "Check the project ID and try again."


class InvalidStateTransitionError(ExHackerError):
    code = "INVALID_TRANSITION"
    message = "This action is not allowed in the current project state."
    status_code = 400


class ResearchFailedError(ExHackerError):
    code = "RESEARCH_FAILED"
    message = "Could not complete research."
    status_code = 502
    suggestion = "Try again in a few minutes, or use cached results."


class BlueprintGenerationError(ExHackerError):
    code = "BLUEPRINT_FAILED"
    message = "Failed to generate blueprint."
    status_code = 500
    suggestion = "Try again. If the issue persists, check your API keys."


class ExportFormatError(ExHackerError):
    code = "UNKNOWN_FORMAT"
    message = "Unsupported export format."
    status_code = 400
    suggestion = "Supported formats: markdown, json."


class AIProviderError(ExHackerError):
    code = "AI_PROVIDER_ERROR"
    message = "AI provider returned an error."
    status_code = 503
    suggestion = "The system will retry automatically. Please wait."


class RateLimitError(ExHackerError):
    code = "RATE_LIMITED"
    message = "Too many requests."
    status_code = 429
    suggestion = "Please wait before making another request."


class AuthError(ExHackerError):
    code = "UNAUTHORIZED"
    message = "Authentication required."
    status_code = 401
    suggestion = "Sign in to access this resource."


# FastAPI exception handler
from fastapi import Request
from fastapi.responses import JSONResponse


async def exhacker_error_handler(request: Request, exc: ExHackerError) -> JSONResponse:
    """Convert ExHackerError to a consistent API response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
                "suggestion": exc.suggestion,
            },
        },
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch all unhandled exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "suggestion": "Please try again. If the issue persists, contact support.",
            },
        },
    )
