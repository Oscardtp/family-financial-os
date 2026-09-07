import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)

FRIENDLY_HTTP_MESSAGES = {
    400: "Los datos enviados no son correctos. Revisa la información e inténtalo de nuevo.",
    401: "Necesitas iniciar sesión para continuar.",
    403: "No tienes permiso para hacer esta acción.",
    404: "No encontramos lo que buscas.",
    405: "Esta acción no está permitida aquí.",
    408: "Se acabó el tiempo. Recarga e inténtalo de nuevo.",
    422: "Revisa los campos marcados. Algo está mal.",
    500: "Algo salió mal de nuestro lado. Inténtalo en un momento.",
    503: "Estamos en mantenimiento. Volvemos en un momento.",
}


def _friendly_detail(status_code: int, default: str) -> str:
    return FRIENDLY_HTTP_MESSAGES.get(status_code, default)


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({"field": loc, "message": error["msg"]})
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "detail": "Los datos enviados no son válidos",
            "fields": errors,
        },
    )


async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = _friendly_detail(exc.status_code, exc.detail or "Ocurrió un error.")
    logger.warning(
        "HTTPException: status=%s path=%s detail=%s",
        exc.status_code,
        request.url.path,
        detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPError",
            "detail": detail,
        },
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: path=%s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "detail": "Algo salió mal de nuestro lado. Inténtalo en un momento.",
        },
    )
