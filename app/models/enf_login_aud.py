from sqlalchemy import Column, String, DateTime, ForeignKey


from app.database.database import Base
from sqlalchemy.orm import relationship


class LoginAudit(Base):

    __tablename__ = "TBL_ENF_LOGIN_AUD"

    audit_id = Column(String(36), primary_key=True)

    user_id = Column(
        String(36),
        ForeignKey("TBL_ENF_USR.USER_ID")
    )

    email = Column(String(255))

    login_result = Column(String(30))

    failure_reason = Column(String(500))

    client_ip = Column(String(100))

    user_agent = Column(String(1000))

    login_ts = Column(DateTime)



    user = relationship(
    "User",
    back_populates="login_audits"
)