from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from app.schemas.user_request import UserRequest
from app.schemas.user_response import UserResponse

from app.dependencies.user_dependencies import get_user_service
from app.services.interfaces.user_service import UserService
from app.dependencies.auth_dependencies import get_current_user
from app.models.enf_user import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
        request: UserRequest,
        user_service: UserService = Depends(
            get_user_service
        )
):

    return user_service.create_user(request)


@router.get(
    "/me",
    response_model=UserResponse
)
def get_current_logged_in_user(
        current_user: User = Depends(get_current_user)
):
    """
    Individually protected endpoint.
    """
    return UserResponse(
        user_id=current_user.user_id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        status=current_user.status
    )