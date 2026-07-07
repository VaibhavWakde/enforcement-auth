from pydantic import BaseModel
from typing import Optional
from app.schemas.user_response import UserResponse


class SignInResponse(BaseModel):
    status: str
    message: str
    otp_required: bool = False
    otp: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = "Bearer"
    user: Optional[UserResponse] = None