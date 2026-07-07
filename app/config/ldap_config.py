from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    USE_ORG_LDAP: bool = False

    # Local OpenLDAP Config
    LOCAL_LDAP_URI: str = "ldap://localhost:389"
    LOCAL_LDAP_BASE_DN: str = "dc=enforcement,dc=local"
    LOCAL_LDAP_BIND_DN: str = "cn=admin,dc=enforcement,dc=local"
    LOCAL_LDAP_BIND_PASSWORD: str = "admin"
    LOCAL_LDAP_USER_BASE: str = "ou=people"
    LOCAL_LDAP_TIMEOUT: int = Field(default=5, description="Timeout in seconds for local LDAP connections")

    # Organization LDAP Config
    ORG_LDAP_URI: str = "ldap://ldap.company.com:389"
    ORG_LDAP_BASE_DN: str = "dc=company,dc=com"
    ORG_LDAP_BIND_DN: str = "cn=service-account,ou=service,dc=company,dc=com"
    ORG_LDAP_BIND_PASSWORD: str = "password"
    ORG_LDAP_USER_BASE: str = "ou=users"
    ORG_LDAP_TIMEOUT: int = Field(default=5, description="Timeout in seconds for organization LDAP connections")

    # Email Config Provider Selector
    USE_ORG_EMAIL_SERVICE: bool = False

    # Local Email Config (SMTP)
    LOCAL_SMTP_HOST: str = "localhost"
    LOCAL_SMTP_PORT: int = 1025
    LOCAL_SMTP_USERNAME: str = ""
    LOCAL_SMTP_PASSWORD: str = ""

    # Splitter API Config (Production AD Email API)
    SPLITTER_BASE_URL: str = "https://api.company.com/email"
    SPLITTER_NOTIFICATION_TYPE: str = "EMAIL"
    SPLITTER_API_KEY: str = ""

    # JWT Config
    JWT_SECRET_KEY: str = "my-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440

    # OTP Config
    OTP_EXPIRATION_MINUTES: int = 5
    OTP_LENGTH: int = 6
    OTP_MAX_RETRY: int = 3

    # CAPTCHA Config
    CAPTCHA_EXPIRATION_MINUTES: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()