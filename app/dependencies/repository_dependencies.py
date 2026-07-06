from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database_dependencies import get_database

from app.repositories.user_repository import UserRepository
from app.repositories.captcha_repository import CaptchaRepository
from app.repositories.otp_repository import OtpRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.login_audit_repository import LoginAuditRepository


def get_user_repository(
        db: Session = Depends(get_database)
) -> UserRepository:
    return UserRepository(db)


def get_captcha_repository(
        db: Session = Depends(get_database)
) -> CaptchaRepository:
    return CaptchaRepository(db)


def get_otp_repository(
        db: Session = Depends(get_database)
) -> OtpRepository:
    return OtpRepository(db)


def get_session_repository(
        db: Session = Depends(get_database)
) -> SessionRepository:
    return SessionRepository(db)


def get_login_audit_repository(
        db: Session = Depends(get_database)
) -> LoginAuditRepository:
    return LoginAuditRepository(db)