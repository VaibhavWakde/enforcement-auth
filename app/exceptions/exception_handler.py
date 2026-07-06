from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.custom_exception import (
    CustomException,
    AuthenticationException,
    ValidationException,
    ResourceNotFoundException,
    BusinessException,
    DatabaseException,
)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers on the FastAPI application.
    """

    @app.exception_handler(AuthenticationException)
    async def authentication_exception_handler(
        request: Request, exc: AuthenticationException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": exc.message,
                "data": exc.data,
            },
        )

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(
        request: Request, exc: ValidationException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": exc.message,
                "data": exc.data,
            },
        )

    @app.exception_handler(ResourceNotFoundException)
    async def resource_not_found_exception_handler(
        request: Request, exc: ResourceNotFoundException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": exc.message,
                "data": exc.data,
            },
        )

    @app.exception_handler(BusinessException)
    async def business_exception_handler(
        request: Request, exc: BusinessException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": exc.message,
                "data": exc.data,
            },
        )

    @app.exception_handler(DatabaseException)
    async def database_exception_handler(
        request: Request, exc: DatabaseException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": exc.message,
                "data": exc.data,
            },
        )

    @app.exception_handler(CustomException)
    async def custom_exception_handler(
        request: Request, exc: CustomException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": exc.error_code,
                "message": exc.message,
                "data": exc.data,
            },
        )
