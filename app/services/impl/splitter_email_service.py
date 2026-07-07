import json
import logging
import urllib.request

from app.config.ldap_config import settings
from app.services.interfaces.email_service import EmailService

logger = logging.getLogger(__name__)


class SplitterEmailService(EmailService):
    """
    Splitter API implementation of EmailService for production environments.
    """

    def _send_via_splitter(self, to_email: str, subject: str, body: str):
        payload = {
            "recipient": to_email,
            "subject": subject,
            "body": body,
            "type": settings.SPLITTER_NOTIFICATION_TYPE
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": settings.SPLITTER_API_KEY
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            settings.SPLITTER_BASE_URL,
            data=data,
            headers=headers,
            method="POST"
        )
        
        try:
            logger.info("SplitterEmailService: Sending request to %s", settings.SPLITTER_BASE_URL)
            with urllib.request.urlopen(req, timeout=5) as response:
                status_code = response.getcode()
                response_body = response.read().decode("utf-8")
                logger.info("SplitterEmailService: Splitter API response status %s: %s", status_code, response_body)
        except Exception as e:
            logger.error("SplitterEmailService: Failed to send email to %s via Splitter API: %s", to_email, str(e))
            raise Exception(f"Failed to send email via Splitter API: {e}")

    def send_login_otp(self, email: str, otp: str):
        subject = "Enforcement Service - Login OTP"
        body = f"Your OTP code is: {otp}. It will expire in {settings.OTP_EXPIRATION_MINUTES} minutes."
        self._send_via_splitter(email, subject, body)

    def send_forgot_password_otp(self, email: str, otp: str):
        subject = "Enforcement Service - Forgot Password OTP"
        body = f"Your Forgot Password OTP code is: {otp}. It will expire in {settings.OTP_EXPIRATION_MINUTES} minutes."
        self._send_via_splitter(email, subject, body)
