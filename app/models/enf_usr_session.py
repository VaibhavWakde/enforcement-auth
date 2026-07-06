from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from app.database.database import Base


class UserSession(Base):
    """
    ORM Model for TBL_ENF_USR_SESSION
    """

    __tablename__ = "TBL_ENF_USR_SESSION"

    session_id = Column(
        "SESSION_ID",
        String(36),
        primary_key=True
    )

    user_id = Column(
        "USER_ID",
        String(36),
        ForeignKey("TBL_ENF_USR.USER_ID"),
        nullable=False
    )

    access_jti = Column(
        "ACCESS_TOKEN_JTI",
        String(100),
        nullable=False
    )

    refresh_jti = Column(
        "REFRESH_TOKEN_JTI",
        String(100),
        nullable=False
    )

    login_time = Column(
        "LOGIN_TIME",
        DateTime
    )

    last_activity_time = Column(
        "LAST_ACTIVITY_TIME",
        DateTime
    )

    logout_time = Column(
        "LOGOUT_TIME",
        DateTime
    )

    is_active = Column(
        "IS_ACTIVE",
        Integer,
        nullable=False,
        default=1
    )

    created_dt = Column(
        "CREATED_DT",
        DateTime
    )

    user = relationship(
        "User",
        back_populates="sessions"
    )

    def __repr__(self):
        return (
            f"<UserSession("
            f"session_id='{self.session_id}', "
            f"user_id='{self.user_id}', "
            f"is_active={self.is_active}"
            f")>"
        )