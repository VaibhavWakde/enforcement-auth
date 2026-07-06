from abc import ABC, abstractmethod


class OtpService(ABC):

    @abstractmethod
    def generate_login_otp(self, user):
        pass

    @abstractmethod
    def verify_otp(self, otp_id, otp):
        pass