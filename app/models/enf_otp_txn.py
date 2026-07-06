from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from app.database.database import Base


class Otp(Base):
    """
    ORM Model for TBL_ENF_OTP_TXN
    """

    __tablename__ = "TBL_ENF_OTP_TXN"

    # ==========================================
    # Primary Key
    # ==========================================

    otp_id = Column(
        "OTP_ID",
        String(36),
        primary_key=True
    )

    # ==========================================
    # Foreign Key
    # ==========================================

    user_id = Column(
        "USER_ID",
        String(36),
        ForeignKey("TBL_ENF_USR.USER_ID"),
        nullable=False
    )

    # ==========================================
    # OTP Details
    # ==========================================

    otp_hash = Column(
        "OTP_HASH",
        String(255),
        nullable=False
    )

    otp_type = Column(
        "OTP_TYPE",
        String(30),
        nullable=False,
        default="LOGIN"
    )

    retry_count = Column(
        "RETRY_COUNT",
        Integer,
        nullable=False,
        default=0
    )

    max_retry_count = Column(
        "MAX_RETRY_COUNT",
        Integer,
        nullable=False,
        default=3
    )

    is_verified = Column(
        "IS_VERIFIED",
        Integer,
        nullable=False,
        default=0
    )

    created_dt = Column(
        "CREATED_DT",
        DateTime,
        nullable=False
    )

    expires_at = Column(
        "EXPIRES_AT",
        DateTime,
        nullable=False
    )

    verified_dt = Column(
        "VERIFIED_DT",
        DateTime
    )

    # ==========================================
    # Relationship
    # ==========================================

    user = relationship(
        "User",
        back_populates="otp_transactions"
    )

    # ==========================================
    # Utility
    # ==========================================

    def __repr__(self):

        return (
            f"<Otp("
            f"otp_id='{self.otp_id}', "
            f"user_id='{self.user_id}', "
            f"otp_type='{self.otp_type}', "
            f"is_verified={self.is_verified}"
            f")>"
        )