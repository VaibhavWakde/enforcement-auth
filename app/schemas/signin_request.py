from pydantic import BaseModel


class SignInRequest(BaseModel):
    username: str
    password: str
    captcha_id: str
    captcha_value: str