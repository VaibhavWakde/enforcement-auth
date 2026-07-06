from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_DSN = os.getenv("DB_DSN")

    SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    ALGORITHM = os.getenv(
        "JWT_ALGORITHM",
        "HS256"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv(
            "JWT_EXPIRY_MINUTES",
            "30"
        )
    )

settings = Settings()