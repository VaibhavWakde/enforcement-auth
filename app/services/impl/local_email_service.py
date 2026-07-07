import logging
import smtplib
from email.mime.text import MIMEText

from app.config.ldap_config import settings
from app.services.interfaces.email_service import EmailService

logger = logging.getLogger(__name__)


class LocalEmailService(EmailService):
    """
    SMTP implementation of EmailService for local development and testing.
    """

    def send_login_otp(self, email: str, otp: str):
        logger.info("LocalEmailService: Sending OTP email to %s", email)
        msg = MIMEText(f"Your OTP code is: {otp}. It will expire in {settings.OTP_EXPIRATION_MINUTES} minutes.")
        msg["Subject"] = "Enforcement Service - Login OTP"
        msg["From"] = "no-reply@enforcement.local"
        msg["To"] = email

        try:
            # Connect to SMTP server
            with smtplib.SMTP(settings.LOCAL_SMTP_HOST, settings.LOCAL_SMTP_PORT, timeout=5) as server:
                if settings.LOCAL_SMTP_USERNAME and settings.LOCAL_SMTP_PASSWORD:
                    server.starttls()
                    server.login(settings.LOCAL_SMTP_USERNAME, settings.LOCAL_SMTP_PASSWORD)
                server.send_message(msg)
            logger.info("LocalEmailService: OTP email successfully sent to %s", email)
        except Exception as e:
            # Log failure but do not crash during local dev if SMTP is not running
            logger.error("LocalEmailService: Failed to send OTP email to %s via SMTP: %s", email, str(e))
            # Fallback printing to console so developer can see the OTP!
            print(f"\n[SMTP OFFLINE FALLBACK] Generated OTP for {email} is: {otp}\n")

    def send_forgot_password_otp(self, email: str, otp: str):
        logger.info("LocalEmailService: Sending forgot password OTP email to %s", email)
        msg = MIMEText(f"Your Forgot Password OTP code is: {otp}. It will expire in {settings.OTP_EXPIRATION_MINUTES} minutes.")
        msg["Subject"] = "Enforcement Service - Forgot Password OTP"
        msg["From"] = "no-reply@enforcement.local"
        msg["To"] = email

        try:
            with smtplib.SMTP(settings.LOCAL_SMTP_HOST, settings.LOCAL_SMTP_PORT, timeout=5) as server:
                if settings.LOCAL_SMTP_USERNAME and settings.LOCAL_SMTP_PASSWORD:
                    server.starttls()
                    server.login(settings.LOCAL_SMTP_USERNAME, settings.LOCAL_SMTP_PASSWORD)
                server.send_message(msg)
            logger.info("LocalEmailService: Forgot password OTP email successfully sent to %s", email)
        except Exception as e:
            logger.error("LocalEmailService: Failed to send forgot password OTP email to %s via SMTP: %s", email, str(e))
            print(f"\n[SMTP OFFLINE FALLBACK] Generated Forgot Password OTP for {email} is: {otp}\n")
