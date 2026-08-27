import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({"field": field, "message": error["msg"]})
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "detail": "Los datos enviados no son válidos",
            "fields": errors,
        },
    )


async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPError",
            "detail": exc.detail,
        },
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "detail": "Ocurrió un error inesperado. Intenta de nuevo.",
        },
    )
