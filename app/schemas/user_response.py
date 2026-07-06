from pydantic import BaseModel


class UserResponse(BaseModel):
    user_id: str
    first_name: str
    last_name: str | None = None
    email: str
    phone_number: str | None = None
    status: str