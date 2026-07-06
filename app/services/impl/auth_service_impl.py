import uuid

from datetime import datetime

from fastapi import Response

from app.models.enf_usr_session import UserSession

from app.repositories.user_repository import UserRepository
from app.repositories.session_repository import SessionRepository

from app.services.interfaces.auth_service import AuthService
from app.services.interfaces.otp_service import OtpService
from app.services.interfaces.email_service import EmailService
from app.services.interfaces.jwt_service import JwtService
from app.services.interfaces.captcha_service import CaptchaService

from app.schemas.signin_request import SignInRequest
from app.schemas.signin_response import SignInResponse
from app.schemas.verify_otp_request import VerifyOtpRequest
from app.schemas.refresh_token_request import RefreshTokenRequest
from app.schemas.token_response import TokenResponse

from app.exceptions.custom_exception import (
    AuthenticationException,
    ValidationException,
)

from app.utils.password_encoder import PasswordEncoder


class AuthServiceImpl(AuthService):

    def __init__(
        self,
        user_repository: UserRepository,
        otp_service: OtpService,
        email_service: EmailService,
        jwt_service: JwtService,
        session_repository: SessionRepository,
        captcha_service: CaptchaService,
    ):
        self.user_repository = user_repository
        self.otp_service = otp_service
        self.email_service = email_service
        self.jwt_service = jwt_service
        self.session_repository = session_repository
        self.captcha_service = captcha_service

    # =========================================================================
    # Sign In
    # =========================================================================

    def signin(
        self,
        request: SignInRequest,
        response: Response
    ) -> SignInResponse:

        # 1. Validate captcha
        self.captcha_service.validate(
            request.captcha_id,
            request.captcha_value
        )

        self.captcha_service.mark_verified(request.captcha_id)

        # 2. Look up user
        user = self.user_repository.find_by_email(request.email)

        if user is None:
            raise AuthenticationException("Invalid email or password")

        if user.status != "ACTIVE":
            raise AuthenticationException(
                f"Account is {user.status.lower()}. Please contact support."
            )

        # 3. Verify password
        if not PasswordEncoder.matches(request.password, user.password_hash):
            raise AuthenticationException("Invalid email or password")

        # 4. Generate OTP and send via email
        otp, otp_id = self.otp_service.generate_login_otp(user)

        # self.email_service.send_otp(user.email, otp)

        response.set_cookie(
            key="otp_txn_id",
            value=otp_id,
            httponly=True,
            secure=False,
            samesite="Lax"
        )

        return SignInResponse(
            status="OTP_SENT",
            message="OTP sent to registered email address",
            otp_required=True,
            otp=otp
        )

    # =========================================================================
    # Verify OTP  →  issue tokens + create session
    # =========================================================================

    def verify_otp(
        self,
        request: VerifyOtpRequest,
        response: Response
    ) -> TokenResponse:

        # 1. Verify OTP
        otp_txn = self.otp_service.verify_otp(
            request.otp_id,
            request.otp
        )

        if otp_txn is None:
            raise AuthenticationException("Invalid or expired OTP")

        # 2. Load user
        user = self.user_repository.find_by_user_id(otp_txn.user_id)

        if user is None:
            raise AuthenticationException("User not found")

        # 3. Deactivate any existing active session
        existing_session = self.session_repository.find_active_session(
            user.user_id
        )

        if existing_session:
            self.session_repository.deactivate(existing_session)

        # 4. Generate tokens
        access_jti = str(uuid.uuid4())
        refresh_jti = str(uuid.uuid4())

        access_token = self.jwt_service.generate_access_token(
            user, access_jti
        )
        refresh_token = self.jwt_service.generate_refresh_token(
            user, refresh_jti
        )

        # 5. Persist session
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

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer"
        )

    # =========================================================================
    # Refresh Token  →  rotate tokens + update session
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
            raise AuthenticationException(
                f"Account is {user.status.lower()}. Please contact support."
            )

        # 4. Rotate tokens
        new_access_jti = str(uuid.uuid4())
        new_refresh_jti = str(uuid.uuid4())

        new_access_token = self.jwt_service.generate_access_token(
            user, new_access_jti
        )
        new_refresh_token = self.jwt_service.generate_refresh_token(
            user, new_refresh_jti
        )

        # 5. Update session
        session.access_jti = new_access_jti
        session.refresh_jti = new_refresh_jti
        session.last_activity_time = datetime.utcnow()

        self.session_repository.update(session)

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