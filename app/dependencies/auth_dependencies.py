from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.dependencies.repository_dependencies import (
    get_user_repository,
    get_session_repository,
)
from app.dependencies.service_dependencies import (
    get_captcha_service,
    get_otp_service,
    get_email_service,
    get_jwt_service,
)

from app.services.impl.auth_service_impl import AuthServiceImpl
from app.services.interfaces.auth_service import AuthService
from app.services.interfaces.jwt_service import JwtService
from app.repositories.user_repository import UserRepository
from app.models.enf_user import User
from app.exceptions.custom_exception import AuthenticationException

_bearer_scheme = HTTPBearer()


def get_auth_service(
    user_repository=Depends(get_user_repository),
    otp_service=Depends(get_otp_service),
    email_service=Depends(get_email_service),
    jwt_service=Depends(get_jwt_service),
    session_repository=Depends(get_session_repository),
    captcha_service=Depends(get_captcha_service),
) -> AuthService:

    return AuthServiceImpl(
        user_repository,
        otp_service,
        email_service,
        jwt_service,
        session_repository,
        captcha_service,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    jwt_service: JwtService = Depends(get_jwt_service),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """
    FastAPI dependency that validates the Bearer token and returns the
    authenticated User ORM object.

    Raises AuthenticationException (HTTP 401) if:
    - The token is missing, malformed, or expired.
    - The token is not an ACCESS token.
    - The user referenced by the token no longer exists.
    """
    token = credentials.credentials

    try:
        payload = jwt_service.verify(token)
    except Exception:
        raise AuthenticationException("Invalid or expired access token")

    if payload.get("type") != "ACCESS":
        raise AuthenticationException("Invalid token type")

    user_id: str = payload.get("sub")
    if not user_id:
        raise AuthenticationException("Invalid token payload")

    user = user_repository.find_by_user_id(user_id)
    if user is None:
        raise AuthenticationException("User not found")

    if user.status != "ACTIVE":
        raise AuthenticationException(
            f"Account is {user.status.lower()}. Please contact support."
        )

    return user
