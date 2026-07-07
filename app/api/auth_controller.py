from fastapi import APIRouter, Depends, Response, Request

from app.schemas.signin_request import SignInRequest
from app.schemas.signin_response import SignInResponse
from app.dependencies.auth_dependencies import get_auth_service
from app.services.interfaces.auth_service import AuthService
from app.schemas.verify_otp_request import VerifyOtpRequest
from app.schemas.refresh_token_request import RefreshTokenRequest
from app.schemas.token_response import TokenResponse

router = APIRouter()


@router.post(
    "/signin",
    response_model=SignInResponse
)
def signin(
        request: SignInRequest,
        response: Response,
        fastapi_req: Request,
        auth_service: AuthService = Depends(get_auth_service)
):
    client_ip = fastapi_req.client.host if fastapi_req.client else None
    user_agent = fastapi_req.headers.get("user-agent")
    return auth_service.signin(
        request=request,
        response=response,
        client_ip=client_ip,
        user_agent=user_agent
    )


@router.post(
    "/verify-otp",
    response_model=TokenResponse
)
def verify_otp(
    request: VerifyOtpRequest,
    response: Response,
    fastapi_req: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    client_ip = fastapi_req.client.host if fastapi_req.client else None
    user_agent = fastapi_req.headers.get("user-agent")
    return auth_service.verify_otp(
        request=request,
        response=response,
        client_ip=client_ip,
        user_agent=user_agent
    )


@router.post(
    "/refresh",
    response_model=TokenResponse
)
def refresh_token(
    request: RefreshTokenRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.refresh_token(request, response)