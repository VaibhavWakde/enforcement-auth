import uuid

from datetime import datetime


from app.schemas.user_request import UserRequest
from app.schemas.user_response import UserResponse
from app.models.enf_user import User
from app.services.interfaces.user_service import UserService
from app.exceptions.custom_exception import ValidationException
from app.utils.password_encoder import PasswordEncoder





class UserServiceImpl(UserService):

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def create_user(
            self,
            request: UserRequest
    ) -> UserResponse:

        existing = self.user_repository.find_by_email(
            request.email
        )

        if existing:
            raise ValidationException(
                "Email already registered."
            )

        password_hash = PasswordEncoder.encode(request.password)

        user = User(
            user_id=str(uuid.uuid4()),
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            phone_number=request.phone_number,
            password_hash=password_hash,
            status="ACTIVE",
            failed_login_count=0,
            created_dt=datetime.utcnow(),
            created_by="SYSTEM"
        )

        saved = self.user_repository.save(user)

        return UserResponse(
            user_id=saved.user_id,
            first_name=saved.first_name,
            last_name=saved.last_name,
            email=saved.email,
            phone_number=saved.phone_number,
            status=saved.status
        )