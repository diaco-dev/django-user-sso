from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.utils.translator import translate


def format_response(error: str, status_code: int, messages: list[str]):
    return {
        "error": error,
        "status_code": status_code,
        "messages": [{"message": translate(msg)} for msg in messages],
    }


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=format_response(
            error=exc.detail,
            status_code=exc.status_code,
            messages=[exc.detail],
        ),
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [error.get("msg", "Validation error") for error in exc.errors()]
    return JSONResponse(
        status_code=422,
        content=format_response(
            error="Validation Error",
            status_code=422,
            messages=errors,
        ),
    )


async def general_exception_handler(request: Request, exc: Exception):
    error_detail = str(exc) if hasattr(exc, "__str__") else repr(exc)
    return JSONResponse(
        status_code=500,
        content=format_response(
            error="Internal server error",
            status_code=500,
            messages=[error_detail if settings.DEBUG else "An unexpected error occurred"],
        ),
    )
