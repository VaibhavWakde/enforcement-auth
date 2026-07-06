from fastapi import Depends

from app.dependencies.repository_dependencies import get_user_repository
from app.repositories.user_repository import UserRepository

from app.services.impl.user_service_impl import UserServiceImpl
from app.services.interfaces.user_service import UserService


def get_user_service(
        user_repository: UserRepository = Depends(
            get_user_repository
        )
) -> UserService:

    return UserServiceImpl(
        user_repository
    )