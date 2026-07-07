import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Add workspace path to sys.path
sys.path.insert(0, "/Users/vaibhav/main/Projects/python/enforcement-auth")

from app.config.ldap_config import settings
from app.services.impl.email_service_factory import EmailServiceFactory
from app.services.impl.local_email_service import LocalEmailService
from app.services.impl.splitter_email_service import SplitterEmailService
from app.services.impl.otp_service_impl import OtpServiceImpl
from app.services.impl.auth_service_impl import AuthServiceImpl
from app.models.enf_otp_txn import Otp
from app.models.enf_user import User
from app.schemas.signin_request import SignInRequest
from app.schemas.verify_otp_request import VerifyOtpRequest
from app.exceptions.custom_exception import AuthenticationException, ValidationException


class TestEmailServiceFactory(unittest.TestCase):
    """
    Test EmailServiceFactory resolves correctly based on config.
    """

    @patch("app.services.impl.email_service_factory.settings")
    def test_factory_resolves_local(self, mock_settings):
        mock_settings.USE_ORG_EMAIL_SERVICE = False
        service = EmailServiceFactory.get_service()
        self.assertIsInstance(service, LocalEmailService)

    @patch("app.services.impl.email_service_factory.settings")
    def test_factory_resolves_splitter(self, mock_settings):
        mock_settings.USE_ORG_EMAIL_SERVICE = True
        service = EmailServiceFactory.get_service()
        self.assertIsInstance(service, SplitterEmailService)


class TestOtpServiceImpl(unittest.TestCase):
    """
    Test brute-force protection, replay protection, and expiration in OtpServiceImpl.
    """

    def setUp(self):
        self.mock_repo = MagicMock()
        self.otp_service = OtpServiceImpl(otp_repository=self.mock_repo)
        self.dummy_user = User(user_id="user-123", email="test@local.dev")

    def test_generate_otp(self):
        otp, otp_id = self.otp_service.generate_login_otp(self.dummy_user)
        self.assertEqual(len(otp), settings.OTP_LENGTH)
        self.assertTrue(self.mock_repo.save.called)

    def test_verify_otp_success(self):
        # Setup verified transaction
        otp_txn = Otp(
            otp_id="otp-123",
            user_id="user-123",
            otp_hash="$2b$12$dummyhash",  # matching '123456'
            is_verified=0,
            retry_count=0,
            max_retry_count=3,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        self.mock_repo.find_by_otp_id.return_value = otp_txn

        with patch("app.services.impl.otp_service_impl.PasswordEncoder.matches", return_value=True):
            res = self.otp_service.verify_otp("otp-123", "123456")
            self.assertEqual(res, otp_txn)
            self.assertTrue(self.mock_repo.mark_verified.called)

    def test_verify_otp_replay_protection(self):
        # find_by_otp_id returns None if already verified or not found
        self.mock_repo.find_by_otp_id.return_value = None
        res = self.otp_service.verify_otp("otp-123", "123456")
        self.assertIsNone(res)

    def test_verify_otp_expired(self):
        otp_txn = Otp(
            otp_id="otp-123",
            user_id="user-123",
            otp_hash="$2b$12$dummyhash",
            is_verified=0,
            retry_count=0,
            max_retry_count=3,
            expires_at=datetime.utcnow() - timedelta(minutes=1)  # expired
        )
        self.mock_repo.find_by_otp_id.return_value = otp_txn
        res = self.otp_service.verify_otp("otp-123", "123456")
        self.assertIsNone(res)

    def test_verify_otp_max_retry_reached(self):
        otp_txn = Otp(
            otp_id="otp-123",
            user_id="user-123",
            otp_hash="$2b$12$dummyhash",
            is_verified=0,
            retry_count=3,  # limit reached
            max_retry_count=3,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        self.mock_repo.find_by_otp_id.return_value = otp_txn
        res = self.otp_service.verify_otp("otp-123", "123456")
        self.assertIsNone(res)

    def test_verify_otp_increment_retries(self):
        otp_txn = Otp(
            otp_id="otp-123",
            user_id="user-123",
            otp_hash="$2b$12$dummyhash",
            is_verified=0,
            retry_count=0,
            max_retry_count=3,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        self.mock_repo.find_by_otp_id.return_value = otp_txn

        with patch("app.services.impl.otp_service_impl.PasswordEncoder.matches", return_value=False):
            res = self.otp_service.verify_otp("otp-123", "wrongcode")
            self.assertIsNone(res)
            self.assertEqual(otp_txn.retry_count, 1)
            self.assertTrue(self.mock_repo.update.called)


class TestAuthServiceImpl(unittest.TestCase):
    """
    Test the AuthServiceImpl signin workflow.
    """

    def setUp(self):
        self.mock_user_repo = MagicMock()
        self.mock_otp_service = MagicMock()
        self.mock_email_service = MagicMock()
        self.mock_jwt_service = MagicMock()
        self.mock_session_repo = MagicMock()
        self.mock_captcha_service = MagicMock()
        self.mock_ldap_service = MagicMock()
        self.mock_audit_repo = MagicMock()

        self.auth_service = AuthServiceImpl(
            user_repository=self.mock_user_repo,
            otp_service=self.mock_otp_service,
            email_service=self.mock_email_service,
            jwt_service=self.mock_jwt_service,
            session_repository=self.mock_session_repo,
            captcha_service=self.mock_captcha_service,
            ldap_service=self.mock_ldap_service,
            login_audit_repository=self.mock_audit_repo
        )

        self.dummy_user = User(
            user_id="user-123",
            email="vaibhav@gmail.com",
            first_name="Vaibhav",
            status="ACTIVE",
            failed_login_count=0
        )

    def test_signin_success_flow(self):
        # 1. Mock Captcha validate
        self.mock_captcha_service.validate.return_value = True
        # 2. Mock User Repository
        self.mock_user_repo.find_by_username_or_email.return_value = self.dummy_user
        # 3. Mock LDAP successful bind
        self.mock_ldap_service.authenticate.return_value = {
            "username": "vaibhav",
            "email": "vaibhav@gmail.com",
            "first_name": "Vaibhav",
            "last_name": "Wakde"
        }
        # 4. Mock OTP generation
        self.mock_otp_service.generate_login_otp.return_value = ("123456", "otp-id-123")

        request = SignInRequest(
            username="vaibhav",
            password="Pass@123",
            captcha_id="captcha-id-abc",
            captcha_value="ABCDEF"
        )
        response = MagicMock()

        res = self.auth_service.signin(request, response, client_ip="127.0.0.1", user_agent="test-agent")

        self.assertEqual(res.status, "SUCCESS")
        self.assertTrue(res.otp_required)
        self.assertEqual(res.otp, "otp-id-123")
        self.mock_email_service.send_login_otp.assert_called_with("vaibhav@gmail.com", "123456")
        self.assertTrue(self.mock_audit_repo.save.called)


if __name__ == "__main__":
    unittest.main()
