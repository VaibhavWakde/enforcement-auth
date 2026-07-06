from abc import ABC, abstractmethod

from app.schemas.user_request import UserRequest
from app.schemas.user_response import UserResponse


class UserService(ABC):

    @abstractmethod
    def create_user(self, request: UserRequest) -> UserResponse:
        pass