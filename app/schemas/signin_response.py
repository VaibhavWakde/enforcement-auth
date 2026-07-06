from pydantic import BaseModel


class SignInResponse(BaseModel):
    status: str
    message: str
    otp_required: bool
    otp: str