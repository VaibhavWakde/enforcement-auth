from fastapi import APIRouter, Depends, Request

from app.dependencies.captcha_dependencies import get_captcha_service
from app.services.interfaces.captcha_service import CaptchaService

router = APIRouter()


@router.get("/generate")

def generate_captcha(

    request: Request,

    captcha_service: CaptchaService = Depends(get_captcha_service)

):

    client_ip = request.client.host

    return captcha_service.generate_captcha(client_ip)