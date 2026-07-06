from pydantic import BaseModel, EmailStr


class UserRequest(BaseModel):
    first_name: str
    last_name: str | None = None
    email: EmailStr
    phone_number: str | None = None
    password: str