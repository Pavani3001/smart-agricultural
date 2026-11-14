"""
Custom exception handlers for the Smart Irrigation API.

Provides consistent error response formatting across all endpoints,
mapping common HTTP errors to a uniform JSON structure.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)


class ResourceNotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, resource_id: int | str):
        self.resource = resource
        self.resource_id = resource_id
        self.message = f"{resource} with id '{resource_id}' not found"
        super().__init__(self.message)


class DuplicateResourceError(Exception):
    """Raised when attempting to create a resource that already exists."""

    def __init__(self, resource: str, detail: str = ""):
        self.resource = resource
        self.message = detail or f"{resource} already exists"
        super().__init__(self.message)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register custom exception handlers on the FastAPI application.

    Ensures all error responses follow a consistent format:
    {"detail": "...", "status_code": <int>}

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(ResourceNotFoundError)
    async def resource_not_found_handler(
        request: Request, exc: ResourceNotFoundError
    ) -> JSONResponse:
        """Handle 404 Not Found errors for missing resources."""
        return JSONResponse(
            status_code=404,
            content={"detail": exc.message, "status_code": 404},
        )

    @app.exception_handler(DuplicateResourceError)
    async def duplicate_resource_handler(
        request: Request, exc: DuplicateResourceError
    ) -> JSONResponse:
        """Handle 409 Conflict errors for duplicate resources."""
        return JSONResponse(
            status_code=409,
            content={"detail": exc.message, "status_code": 409},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle 422 Validation errors with a simplified error message.

        Extracts the first validation error detail for readability.
        """
        errors = exc.errors()
        # Build a human-readable summary of validation failures
        details = "; ".join(
            f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}"
            for e in errors
        )
        return JSONResponse(
            status_code=422,
            content={"detail": f"Validation error: {details}", "status_code": 422},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Handle all other HTTPExceptions with consistent format."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc.detail), "status_code": exc.status_code},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Catch-all handler for unhandled 500 Internal Server errors.

        Logs the full traceback for debugging while returning a safe
        message to the client.
        """
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal server error occurred.",
                "status_code": 500,
            },
        )
