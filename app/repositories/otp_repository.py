from sqlalchemy.orm import Session

from app.models.enf_otp_txn import Otp
from datetime import datetime


class OtpRepository:

    def __init__(self, db: Session):
        self.db = db

    def save(self, otp: Otp):
        self.db.add(otp)
        self.db.commit()
        self.db.refresh(otp)
        return otp

    def find_active_otp(self, user_id: str):
        return (
            self.db.query(Otp)
            .filter(
                Otp.user_id == user_id,
                Otp.is_verified == 0
            )
            .order_by(Otp.created_dt.desc())
            .first()
        )

    def find_by_otp_id(self, otp_id: str):
        return (
            self.db.query(Otp)
            .filter(
                Otp.otp_id == otp_id,
                Otp.is_verified == 0
            )
            .first()
        )

    def mark_verified(self, otp: Otp):
        otp.is_verified = 1
        otp.verified_dt = datetime.utcnow()

        self.db.commit()
    
    def update(self, otp):

        self.db.commit()

        self.db.refresh(otp)

        return otp