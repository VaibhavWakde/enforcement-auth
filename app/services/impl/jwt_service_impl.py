import jwt

from datetime import datetime
import uuid

from app.config.jwt_config import (
    JWT_SECRET,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE,
    REFRESH_TOKEN_EXPIRE
)

from app.services.interfaces.jwt_service import JwtService
from app.exceptions.custom_exception import AuthenticationException


class JwtServiceImpl(JwtService):

    def generate_access_token(self, user, access_jti):

        payload = {
            "sub": user.user_id,
            "email": user.email,
            "jti": access_jti,
            "type": "ACCESS",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRE
        }

        return jwt.encode(
            payload,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )

    def generate_refresh_token(self, user, refresh_jti):

        payload = {
            "sub": user.user_id,
            "jti": refresh_jti,
            "type": "REFRESH",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + REFRESH_TOKEN_EXPIRE
        }

        return jwt.encode(
            payload,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )

    def extract_jti(self, token):

        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        return payload["jti"]

    def verify(self, token):

        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

    def extract_email(self, token: str):
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        return payload["email"]

    def verify_access_token_and_extract_username(self, token: str) -> str:
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )
            
            # Ensure it is an access token
            if payload.get("type") != "ACCESS":
                raise AuthenticationException("Invalid token type")
                
            return payload["email"]
        except jwt.ExpiredSignatureError:
            raise AuthenticationException("Access token has expired")
        except jwt.PyJWTError:
            raise AuthenticationException("Invalid access token")