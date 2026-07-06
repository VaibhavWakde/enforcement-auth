from typing import Any, Optional


class CustomException(Exception):
    """
    Base exception for the application.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "APP-500",
        status_code: int = 500,
        data: Optional[Any] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.data = data

        super().__init__(message)


class AuthenticationException(CustomException):
    """
    Authentication related exceptions.
    """

    def __init__(
        self,
        message: str = "Authentication Failed",
        error_code: str = "AUTH-401",
        data: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=401,
            data=data
        )


class ValidationException(CustomException):
    """
    Request validation exceptions.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "VAL-400",
        data: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=400,
            data=data
        )


class ResourceNotFoundException(CustomException):
    """
    Resource not found exceptions.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "RES-404",
        data: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=404,
            data=data
        )


class BusinessException(CustomException):
    """
    Business rule validation exceptions.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "BUS-400",
        data: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=400,
            data=data
        )


class DatabaseException(CustomException):
    """
    Database related exceptions.
    """

    def __init__(
        self,
        message: str = "Database Error",
        error_code: str = "DB-500",
        data: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=500,
            data=data
        )