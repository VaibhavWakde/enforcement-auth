from abc import ABC, abstractmethod


class CaptchaService(ABC):

    @abstractmethod
    def generate_captcha(self, client_ip: str):
        """
        Generate captcha image and persist it.
        """
        pass

    @abstractmethod
    def validate(
        self,
        captcha_id: str,
        captcha_value: str
    ):
        """
        Validate captcha entered by the user.
        """
        pass

    @abstractmethod
    def mark_verified(
        self,
        captcha_id: str
    ):
        """
        Mark captcha as verified.
        """
        pass