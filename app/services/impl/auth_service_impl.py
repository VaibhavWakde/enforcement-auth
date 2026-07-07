import uuid
import logging
from datetime import datetime
from typing import Optional

from fastapi import Response

from app.models.enf_usr_session import UserSession
from app.models.enf_user import User
from app.models.enf_login_aud import LoginAudit

from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.login_audit_repository import LoginAuditRepository

from app.services.interfaces.auth_service import AuthService
from app.services.interfaces.otp_service import OtpService
from app.services.interfaces.email_service import EmailService
from app.services.interfaces.jwt_service import JwtService
from app.services.interfaces.captcha_service import CaptchaService
from app.services.interfaces.ldap_service import LDAPService

from app.schemas.signin_request import SignInRequest
from app.schemas.signin_response import SignInResponse
from app.schemas.verify_otp_request import VerifyOtpRequest
from app.schemas.refresh_token_request import RefreshTokenRequest
from app.schemas.token_response import TokenResponse
from app.schemas.user_response import UserResponse

from app.exceptions.custom_exception import (
    AuthenticationException,
    ValidationException,
)
from app.utils.password_encoder import PasswordEncoder

logger = logging.getLogger(__name__)


class AuthServiceImpl(AuthService):
    """
    Production-ready AuthService enforcing Clean Architecture and SOLID.
    Manages CAPTCHA, local DB user lookup, LDAP binding, OTP generation/email dispatch,
    database audit logging, and session/JWT issuance upon successful verification.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        otp_service: OtpService,
        email_service: EmailService,
        jwt_service: JwtService,
        session_repository: SessionRepository,
        captcha_service: CaptchaService,
        ldap_service: LDAPService,
        login_audit_repository: LoginAuditRepository
    ):
        self.user_repository = user_repository
        self.otp_service = otp_service
        self.email_service = email_service
        self.jwt_service = jwt_service
        self.session_repository = session_repository
        self.captcha_service = captcha_service
        self.ldap_service = ldap_service
        self.login_audit_repository = login_audit_repository

    def _save_audit(
        self,
        login_result: str,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        failure_reason: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Helper method to persist authentication audit log events.
        """
        try:
            audit = LoginAudit(
                audit_id=str(uuid.uuid4()),
                user_id=user_id,
                email=email,
                login_result=login_result,
                failure_reason=failure_reason,
                client_ip=client_ip,
                user_agent=user_agent,
                login_ts=datetime.utcnow()
            )
            self.login_audit_repository.save(audit)
            logger.info("AuthService Audit: Logged %s for email=%s", login_result, email)
        except Exception as e:
            logger.error("AuthService Audit Error: Failed to write audit record: %s", str(e), exc_info=True)

    # =========================================================================
    # Sign In (Phase 1: CAPTCHA -> DB Lookup -> LDAP -> OTP -> Email)
    # =========================================================================

    def signin(
        self,
        request: SignInRequest,
        response: Response,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> SignInResponse:
        
        # 1. Validate CAPTCHA first (no DB or LDAP calls should trigger if this fails)
        try:
            self.captcha_service.validate(request.captcha_id, request.captcha_value)
            self.captcha_service.mark_verified(request.captcha_id)
        except ValidationException as ve:
            self._save_audit(
                login_result="FAILED",
                email=request.username,
                failure_reason=f"CAPTCHA validation failed: {str(ve)}",
                client_ip=client_ip,
                user_agent=user_agent
            )
            raise ve

        # 2. Look up the user locally in the application database by email or username
        user = self.user_repository.find_by_username_or_email(request.username)
        if user is None:
            self._save_audit(
                login_result="FAILED",
                email=request.username,
                failure_reason="User not found in local database",
                client_ip=client_ip,
                user_agent=user_agent
            )
            # Obfuscated error message to prevent username enumeration
            raise AuthenticationException("Invalid username or password")

        # Check if user status is ACTIVE
        if user.status != "ACTIVE":
            self._save_audit(
                login_result="FAILED",
                user_id=user.user_id,
                email=user.email,
                failure_reason=f"Account is in status: {user.status}",
                client_ip=client_ip,
                user_agent=user_agent
            )
            raise AuthenticationException(f"Account is {user.status.lower()}. Please contact support.")

        # 3. Authenticate user credentials against LDAP provider
        ldap_user = self.ldap_service.authenticate(request.username, request.password)
        if not ldap_user:
            # Increment failed login attempts
            user.failed_login_count += 1
            self.user_repository.update()

            self._save_audit(
                login_result="FAILED",
                user_id=user.user_id,
                email=user.email,
                failure_reason="LDAP bind/authentication failed",
                client_ip=client_ip,
                user_agent=user_agent
            )
            raise AuthenticationException("Invalid username or password")

        # Successful LDAP bind: reset failed login count and sync attributes if modified
        user.failed_login_count = 0
        user.first_name = ldap_user.get("first_name", user.first_name)
        user.last_name = ldap_user.get("last_name", user.last_name)
        user.phone_number = ldap_user.get("phone_number", user.phone_number)
        user.updated_dt = datetime.utcnow()
        user.updated_by = "LDAP"
        self.user_repository.update()

        # 4. Generate OTP
        try:
            otp, otp_id = self.otp_service.generate_login_otp(user)
            
        except Exception as e:
            logger.error("AuthService: Failed to generate OTP: %s", str(e), exc_info=True)
            self._save_audit(
                login_result="FAILED",
                user_id=user.user_id,
                email=user.email,
                failure_reason=f"OTP generation error: {str(e)}",
                client_ip=client_ip,
                user_agent=user_agent
            )
            raise AuthenticationException("Could not complete signin process. Please try again.")

        # 5. Send OTP using Email Service Factory
        try:
            self.email_service.send_login_otp(user.email, otp)
        except Exception as e:
            logger.error("AuthService: Failed to send OTP email: %s", str(e), exc_info=True)
            self._save_audit(
                login_result="FAILED",
                user_id=user.user_id,
                email=user.email,
                failure_reason=f"Email dispatch error: {str(e)}",
                client_ip=client_ip,
                user_agent=user_agent
            )
            raise AuthenticationException("Failed to send verification code. Please check server logs.")

        # Log OTP_SENT Audit Log
        self._save_audit(
            login_result="OTP_SENT",
            user_id=user.user_id,
            email=user.email,
            client_ip=client_ip,
            user_agent=user_agent
        )

        response.set_cookie(
            key="otp_id",
            value=otp_id,
            httponly=True,
            secure=False,
            samesite="Lax"
        )

        return SignInResponse(
            status="SUCCESS",
            message="Verification code sent to your registered email address.",
            otp_required=True,
            otp=otp_id
        )

    # =========================================================================
    # Verify OTP (Phase 2: Verify OTP -> JWT Generation -> Session -> Cookies)
    # =========================================================================

    def verify_otp(
        self,
        request: VerifyOtpRequest,
        response: Response,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponse:

        # 1. Verify OTP
        otp_txn = self.otp_service.verify_otp(request.otp_id, request.otp)
        if otp_txn is None:
            # We don't have user_id if txn is invalid, but we lookup the OTP record to get user email if possible
            self._save_audit(
                login_result="FAILED",
                failure_reason="Invalid, expired or max-retried OTP code submitted",
                client_ip=client_ip,
                user_agent=user_agent
            )
            raise AuthenticationException("Invalid or expired OTP")

        # 2. Load user
        user = self.user_repository.find_by_user_id(otp_txn.user_id)
        if user is None:
            self._save_audit(
                login_result="FAILED",
                failure_reason="User associated with verified OTP does not exist",
                client_ip=client_ip,
                user_agent=user_agent
            )
            raise AuthenticationException("User not found")

        # 3. Deactivate any existing active session
        existing_session = self.session_repository.find_active_session(user.user_id)
        if existing_session:
            self.session_repository.deactivate(existing_session)

        # 4. Generate JWT tokens
        access_jti = str(uuid.uuid4())
        refresh_jti = str(uuid.uuid4())

        access_token = self.jwt_service.generate_access_token(user, access_jti)
        refresh_token = self.jwt_service.generate_refresh_token(user, refresh_jti)

        # 5. Persist Session
        session = UserSession(
            session_id=str(uuid.uuid4()),
            user_id=user.user_id,
            access_jti=access_jti,
            refresh_jti=refresh_jti,
            login_time=datetime.utcnow(),
            last_activity_time=datetime.utcnow(),
            is_active=1,
            created_dt=datetime.utcnow(),
        )
        self.session_repository.save(session)

        # 6. Set HTTP-Only Cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="Lax"
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax"
        )

        # Write SUCCESS audit log
        self._save_audit(
            login_result="SUCCESS",
            user_id=user.user_id,
            email=user.email,
            client_ip=client_ip,
            user_agent=user_agent
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer"
        )

    # =========================================================================
    # Refresh Token (Rotate Tokens -> Update Session -> Update Cookies)
    # =========================================================================

    def refresh_token(
        self,
        request: RefreshTokenRequest,
        response: Response
    ) -> TokenResponse:

        # 1. Decode and validate the refresh token
        try:
            payload = self.jwt_service.verify(request.refresh_token)
        except Exception:
            raise AuthenticationException("Invalid or expired refresh token")

        if payload.get("type") != "REFRESH":
            raise AuthenticationException("Invalid token type")

        refresh_jti = payload.get("jti")
        user_id = payload.get("sub")

        # 2. Look up active session by refresh JTI
        session = self.session_repository.find_by_refresh_jti(refresh_jti)
        if session is None:
            raise AuthenticationException("Session not found or expired")

        # 3. Load user
        user = self.user_repository.find_by_user_id(user_id)
        if user is None:
            raise AuthenticationException("User not found")

        if user.status != "ACTIVE":
            raise AuthenticationException(f"Account is {user.status.lower()}. Please contact support.")

        # 4. Rotate tokens
        new_access_jti = str(uuid.uuid4())
        new_refresh_jti = str(uuid.uuid4())

        new_access_token = self.jwt_service.generate_access_token(user, new_access_jti)
        new_refresh_token = self.jwt_service.generate_refresh_token(user, new_refresh_jti)

        # 5. Update session
        session.access_jti = new_access_jti
        session.refresh_jti = new_refresh_jti
        session.last_activity_time = datetime.utcnow()

        self.session_repository.update(session)

        # 6. Set HTTP-Only Cookies
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=False,
            samesite="Lax"
        )
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax"
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="Bearer"
        )