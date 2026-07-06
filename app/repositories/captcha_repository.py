from sqlalchemy.orm import Session

from app.models.enf_captcha_txn import EnfCaptchaTxn


class CaptchaRepository:

    def __init__(self, db: Session):
        self.db = db

    def save(self, captcha: EnfCaptchaTxn):
        self.db.add(captcha)
        self.db.commit()
        self.db.refresh(captcha)
        return captcha

    def find_by_id(self, captcha_id: str):
        return (
            self.db.query(EnfCaptchaTxn)
            .filter(EnfCaptchaTxn.captcha_id == captcha_id)
            .first()
        )

    # def update(self):
    #     self.db.commit()

    def update(self, captcha):
        self.db.add(captcha)
        self.db.commit()
        self.db.refresh(captcha)
        return captcha

    def delete(self, captcha: EnfCaptchaTxn):
        self.db.delete(captcha)
        self.db.commit()