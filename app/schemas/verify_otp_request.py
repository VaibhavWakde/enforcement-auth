from pydantic import BaseModel


class VerifyOtpRequest(BaseModel):
    otp_id: str
    otp: str