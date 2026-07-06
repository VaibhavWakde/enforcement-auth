from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

# Configure the password hasher
password_hasher = PasswordHasher(
    time_cost=3,      # Number of iterations
    memory_cost=65536, # 64 MB
    parallelism=4,
    hash_len=32,
    salt_len=16
)


class PasswordUtil:

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain-text password.
        """
        return password_hasher.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a plain-text password against the stored Argon2 hash.
        """
        try:
            return password_hasher.verify(hashed_password, password)
        except (VerifyMismatchError, VerificationError):
            return False
        

