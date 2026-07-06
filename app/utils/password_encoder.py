import bcrypt


class PasswordEncoder:

    @staticmethod
    def encode(password: str) -> str:
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    @staticmethod
    def matches(raw_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            raw_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )