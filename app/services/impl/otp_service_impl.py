import uuid
import random

from datetime import datetime
from datetime import timedelta

from passlib.context import CryptContext

from app.models.enf_otp_txn import Otp
from app.services.interfaces.otp_service import OtpService
from app.utils.password_encoder import PasswordEncoder


# pwd_context = CryptContext(
#     schemes=["bcrypt"],
#     deprecated="auto"
# )


class OtpServiceImpl(OtpService):

    def __init__(self, otp_repository):
        self.otp_repository = otp_repository

    def generate_login_otp(self, user) -> tuple[str, str]:

        otp = str(random.randint(100000, 999999))
        otp_id = str(uuid.uuid4())

        otp_entity = Otp(
            otp_id=otp_id,
            user_id=user.user_id,
            otp_hash=PasswordEncoder.encode(otp),
            otp_type="LOGIN",
            retry_count=0,
            max_retry_count=3,
            is_verified=0,
            created_dt=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )

        self.otp_repository.save(otp_entity)

        return otp, otp_id

    def verify_otp(
        self,
        otp_id: str,
        otp: str
    ) -> Otp | None:

        otp_txn = self.otp_repository.find_by_otp_id(otp_id)

        if otp_txn is None:
            return None

        if otp_txn.expires_at < datetime.utcnow():
            return None

        # if not pwd_context.verify(
        #     otp,
        #     otp_txn.otp_hash
        # ):
        #     return None
        
        if not PasswordEncoder.matches(
            otp,
            otp_txn.otp_hash
        ):
            return None

        self.otp_repository.mark_verified(
            otp_txn
        )

        return otp_txn