import uuid
import random
import string
import logging
from datetime import datetime, timedelta

from app.config.ldap_config import settings
from app.models.enf_otp_txn import Otp
from app.services.interfaces.otp_service import OtpService
from app.utils.password_encoder import PasswordEncoder

logger = logging.getLogger(__name__)


class OtpServiceImpl(OtpService):
    """
    Production-grade OTP Service with brute-force protection, replay protection,
    dynamic expiry, and configurable lengths.
    """

    def __init__(self, otp_repository):
        self.otp_repository = otp_repository

    def generate_login_otp(self, user) -> tuple[str, str]:
        # Generate dynamic numeric OTP code of configured length
        otp_length = settings.OTP_LENGTH
        otp = "".join(random.choices(string.digits, k=otp_length))
        otp_id = str(uuid.uuid4())

        expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)

        otp_entity = Otp(
            otp_id=otp_id,
            user_id=user.user_id,
            otp_hash=PasswordEncoder.encode(otp),
            otp_type="LOGIN",
            retry_count=0,
            max_retry_count=settings.OTP_MAX_RETRY,
            is_verified=0,
            created_dt=datetime.utcnow(),
            expires_at=expires_at
        )

        self.otp_repository.save(otp_entity)
        logger.info("OtpService: Generated OTP transaction ID %s for user ID %s (expires at %s)", otp_id, user.user_id, expires_at)
        return otp, otp_id

    def verify_otp(self, otp_id: str, otp: str) -> Otp | None:
        # Note: self.otp_repository.find_by_otp_id only returns unverified OTP records
        otp_txn = self.otp_repository.find_by_otp_id(otp_id)

        if otp_txn is None:
            logger.warning("OtpService: OTP transaction %s not found or already verified (replay attempt)", otp_id)
            return None

        # Expiry Check
        if otp_txn.expires_at < datetime.utcnow():
            logger.warning("OtpService: OTP transaction %s has expired", otp_id)
            return None

        # Brute Force / Max Retry Check
        if otp_txn.retry_count >= otp_txn.max_retry_count:
            logger.warning("OtpService: OTP transaction %s exceeded max retry count", otp_id)
            return None

        # Verify Hash
        if not PasswordEncoder.matches(otp, otp_txn.otp_hash):
            otp_txn.retry_count += 1
            self.otp_repository.update(otp_txn)
            logger.warning("OtpService: OTP verification failed for txn %s. Incrementing retry count to %d/%d", 
                           otp_id, otp_txn.retry_count, otp_txn.max_retry_count)
            return None

        # Mark OTP as verified (automatically invalidates/prevents replay attacks)
        self.otp_repository.mark_verified(otp_txn)
        logger.info("OtpService: OTP transaction %s verified successfully", otp_id)
        return otp_txn