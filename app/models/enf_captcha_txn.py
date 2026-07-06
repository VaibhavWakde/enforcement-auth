from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Integer

from app.database.database import Base


class EnfCaptchaTxn(Base):
    """
    ORM Model for TBL_ENF_CAP_TXN
    """

    __tablename__ = "TBL_ENF_CAP_TXN"

    # ==========================
    # Primary Key
    # ==========================

    captcha_id = Column(
        "CAPTCHA_ID",
        String(36),
        primary_key=True
    )

    # ==========================
    # Captcha Details
    # ==========================

    captcha_value = Column(
        "CAPTCHA_VALUE",
        String(20),
        nullable=False
    )

    client_ip = Column(
        "CLIENT_IP",
        String(100)
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

    def __repr__(self):
        return (
            f"<EnfCaptchaTxn("
            f"captcha_id='{self.captcha_id}', "
            f"is_verified={self.is_verified})>"
        )