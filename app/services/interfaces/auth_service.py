from abc import ABC, abstractmethod
from fastapi import Response
from app.schemas.signin_request import SignInRequest
from app.schemas.signin_response import SignInResponse
from app.schemas.verify_otp_request import VerifyOtpRequest
from app.schemas.refresh_token_request import RefreshTokenRequest

from app.schemas.token_response import TokenResponse


class AuthService(ABC):

    @abstractmethod
    def signin(self, request: SignInRequest, response: Response) -> SignInResponse:
        pass

    # @abstractmethod
    # def verify_otp(
    #     self,
    #     request: VerifyOtpRequest
    # ):
    #     pass

    @abstractmethod
    def verify_otp(
        self,
        request: VerifyOtpRequest,
        response: Response
    ):
        pass


    @abstractmethod
    def refresh_token(
        self,
        request: RefreshTokenRequest,
        response: Response
    ) -> TokenResponse:
        pass

    # @abstractmethod
    # def refresh_token(self):
    #     pass

    # @abstractmethod
    # def logout(self):
    #     pass