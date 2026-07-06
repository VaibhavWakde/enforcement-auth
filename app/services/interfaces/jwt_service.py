from abc import ABC, abstractmethod


class JwtService(ABC):

    @abstractmethod
    def generate_access_token(self, user, access_jti):
        pass

    @abstractmethod
    def generate_refresh_token(self, user, refresh_jti):
        pass

    @abstractmethod
    def extract_jti(self, token):
        pass

    @abstractmethod
    def verify(self, token):
        pass

    @abstractmethod
    def extract_email(self, token):
        pass