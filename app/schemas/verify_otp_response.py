from pydantic import BaseModel


class VerifyOtpResponse(BaseModel):
    status: str
    message: str
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"