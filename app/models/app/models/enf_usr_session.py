from sqlalchemy import Column, String, DateTime
from app.config.database import Base


class UserSession(Base):

    __tablename__ = "TBL_ENF_USR_SESSION"

    session_id = Column(String(36), primary_key=True)

    user_id = Column(String(50), nullable=False)

    access_token = Column(String(4000), nullable=False)

    refresh_token = Column(String(4000), nullable=False)

    access_jti = Column(String(36), nullable=False)

    refresh_jti = Column(String(36), nullable=False)

    created_at = Column(DateTime)

    expires_at = Column(DateTime)

    status = Column(String(20))