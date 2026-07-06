from fastapi import Depends

from app.dependencies.repository_dependencies import get_captcha_repository

from app.repositories.captcha_repository import CaptchaRepository

from app.services.interfaces.captcha_service import CaptchaService
from app.services.impl.captcha_service_impl import CaptchaServiceImpl


def get_captcha_service(
    repository: CaptchaRepository = Depends(get_captcha_repository)
) -> CaptchaService:

    return CaptchaServiceImpl(repository)