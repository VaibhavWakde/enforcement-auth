from fastapi import APIRouter, Depends, Response

from app.schemas.signin_request import SignInRequest
from app.schemas.signin_response import SignInResponse
from app.dependencies.auth_dependencies import get_auth_service
from app.services.interfaces.auth_service import AuthService
from app.schemas.verify_otp_request import VerifyOtpRequest
from app.schemas.refresh_token_request import RefreshTokenRequest

router = APIRouter()



@router.post(
    "/signin",
    response_model=SignInResponse
)
def signin(
        request: SignInRequest,
        response: Response,
        auth_service: AuthService = Depends(get_auth_service)
):

    return auth_service.signin(request, response)




# @router.post("/verify-otp")
# def verify_otp(
#     request: VerifyOtpRequest,
#     auth_service: AuthService = Depends(get_auth_service)
# ):
#     return auth_service.verify_otp(request)


@router.post("/verify-otp")
def verify_otp(
    request: VerifyOtpRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.verify_otp(
        request,
        response
    )


@router.post("/refresh")
def refresh_token(
    request: RefreshTokenRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.refresh_token(request, response)