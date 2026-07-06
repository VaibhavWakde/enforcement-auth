from abc import ABC, abstractmethod


class EmailService(ABC):

    @abstractmethod
    def send_login_otp(
        self,
        email: str,
        otp: str
    ):
        pass

    @abstractmethod
    def send_forgot_password_otp(
        self,
        email: str,
        otp: str
    ):
        pass