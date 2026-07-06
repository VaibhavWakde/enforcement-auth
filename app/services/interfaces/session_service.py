from abc import ABC, abstractmethod


class SessionService(ABC):

    @abstractmethod
    def create_session(self, user, client_ip, user_agent):
        pass

    @abstractmethod
    def deactivate_previous_session(self, user_id):
        pass

    @abstractmethod
    def refresh_session(self, refresh_jti):
        pass