from fastapi import Depends

from app.dependencies.repository_dependencies import *

from app.services.impl.captcha_service_impl import CaptchaServiceImpl
from app.services.impl.otp_service_impl import OtpServiceImpl
from app.services.impl.email_service_impl import EmailServiceImpl

from app.services.interfaces.captcha_service import CaptchaService
from app.services.interfaces.otp_service import OtpService
from app.services.interfaces.email_service import EmailService

from app.services.impl.jwt_service_impl import JwtServiceImpl

from app.services.interfaces.jwt_service import JwtService


def get_captcha_service(
        captcha_repository=Depends(get_captcha_repository)
) -> CaptchaService:

    return CaptchaServiceImpl(captcha_repository)


def get_otp_service(
        otp_repository=Depends(get_otp_repository)
) -> OtpService:

    return OtpServiceImpl(otp_repository)


def get_email_service() -> EmailService:

    return EmailServiceImpl()


def get_jwt_service() -> JwtService:

    return JwtServiceImpl()