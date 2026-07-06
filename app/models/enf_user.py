from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    """
    ORM Model for TBL_ENF_USR
    """

    __tablename__ = "TBL_ENF_USR"

    # ==========================
    # Primary Key
    # ==========================
    user_id = Column(
        "USER_ID",
        String(36),
        primary_key=True
    )

    # ==========================
    # User Information
    # ==========================
    first_name = Column(
        "FIRST_NAME",
        String(100),
        nullable=False
    )

    last_name = Column(
        "LAST_NAME",
        String(100)
    )

    email = Column(
        "EMAIL",
        String(255),
        nullable=False,
        unique=True
    )

    phone_number = Column(
        "PHONE_NUMBER",
        String(20)
    )

    password_hash = Column(
        "PASSWORD_HASH",
        String(255),
        nullable=False
    )

    # ==========================
    # Status
    # ==========================
    status = Column(
        "STATUS",
        String(20),
        nullable=False,
        default="ACTIVE"
    )

    failed_login_count = Column(
        "FAILED_LOGIN_COUNT",
        Integer,
        nullable=False,
        default=0
    )

    last_login_ts = Column(
        "LAST_LOGIN_TS",
        DateTime
    )

    password_changed_dt = Column(
        "PASSWORD_CHANGED_DT",
        DateTime
    )

    status_changed_dt = Column(
        "STATUS_CHANGED_DT",
        DateTime
    )

    # ==========================
    # Audit
    # ==========================
    created_dt = Column(
        "CREATED_DT",
        DateTime
    )

    created_by = Column(
        "CREATED_BY",
        String(100)
    )

    updated_dt = Column(
        "UPDATED_DT",
        DateTime
    )

    updated_by = Column(
        "UPDATED_BY",
        String(100)
    )

    # ==========================
    # Relationships
    # ==========================
    otp_transactions = relationship(
        "Otp",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    login_audits = relationship(
        "LoginAudit",
        back_populates="user"
    )