from app.api import captcha_controller
import base64
import hashlib
import random
import string
import uuid
from datetime import datetime, timedelta
from io import BytesIO

from captcha.image import ImageCaptcha

from app.exceptions.custom_exception import ValidationException
from app.models.enf_captcha_txn import EnfCaptchaTxn
from app.repositories.captcha_repository import CaptchaRepository
from app.services.interfaces.captcha_service import CaptchaService


class CaptchaServiceImpl(CaptchaService):

    CAPTCHA_LENGTH = 6
    CAPTCHA_EXPIRY_MINUTES = 5

    # Excluding confusing characters:
    # O, 0, I, 1, L
    CAPTCHA_CHARSET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

    def __init__(self, repository: CaptchaRepository):
        self.repository = repository

    def _generate_captcha_text(self) -> str:
        """
        Generates a random alphanumeric captcha.
        """
        return "".join(
            random.choices(
                self.CAPTCHA_CHARSET,
                k=self.CAPTCHA_LENGTH
            )
        )

    def _hash_captcha(self, captcha: str) -> str:
        return hashlib.sha256(
            captcha.upper().encode("utf-8")
        ).hexdigest()

    def generate_captcha(self, client_ip: str):

        captcha_text = ''.join(
            random.choices(string.ascii_letters + string.digits, k=6)
        )

        image = ImageCaptcha()

        buffer = BytesIO()
        image.write(captcha_text, buffer)

        image_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        captcha = EnfCaptchaTxn(
            captcha_id=str(uuid.uuid4()),
            captcha_value=self._hash_captcha(captcha_text),
            client_ip=client_ip,
            is_verified=0,
            created_dt=datetime.utcnow(),
            expires_at=datetime.utcnow()
            + timedelta(minutes=self.CAPTCHA_EXPIRY_MINUTES)
        )

        self.repository.save(captcha)

        return {
            "captcha_id": captcha.captcha_id,
            # Uncomment during development only
            "captcha": captcha_text,

            # Use image in production
            # "captcha_image": image_base64
        }

    def validate(
        self,
        captcha_id: str,
        captcha_value: str
    ) -> bool:

        captcha = self.repository.find_by_id(
            captcha_id
        )

        if captcha is None:
            raise ValidationException(
                "Captcha not found."
            )

        if captcha.is_verified == 1:
            raise ValidationException(
                "Captcha has already been used."
            )

        if captcha.expires_at < datetime.utcnow():
            raise ValidationException(
                "Captcha has expired."
            )

        entered_hash = self._hash_captcha(
            captcha_value.strip()
        )

        if entered_hash != captcha.captcha_value:
            raise ValidationException(
                "Invalid captcha."
            )

        return True

    def mark_verified(
        self,
        captcha_id: str
    ):

        captcha = self.repository.find_by_id(
            captcha_id
        )

        if captcha is None:
            raise ValidationException(
                "Captcha not found."
            )

        captcha.is_verified = 1
        captcha.verified_dt = datetime.utcnow()

        self.repository.update(captcha)