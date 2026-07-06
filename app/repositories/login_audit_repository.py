from sqlalchemy.orm import Session

from app.models.enf_login_aud import LoginAudit


class LoginAuditRepository:

    def __init__(self, db: Session):
        self.db = db

    def save(self, audit: LoginAudit):
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit