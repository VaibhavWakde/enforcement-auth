import uuid
import random
import string
import base64

from datetime import datetime
from datetime import timedelta

from captcha.image import ImageCaptcha
from sqlalchemy.orm import Session

from app.models.enf_captcha_txn import EnfCaptchaTxn


class CaptchaService:

    @staticmethod
    def generate_captcha(db: Session):

        captcha_text = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )

        captcha_id = str(uuid.uuid4())

        image = ImageCaptcha()

        image_data = image.generate(
            captcha_text
        )

        image_bytes = image_data.read()

        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        captcha_entity = EnfCaptchaTxn(
            captcha_id=captcha_id,
            captcha_value=captcha_text,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=2),
            is_verified=False
        )

        db.add(captcha_entity)

        db.commit()

        return {
            "captchaId": captcha_id,
            "captchaImage": image_base64,
            "captcha": captcha_text
        }   