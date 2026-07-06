# from sqlalchemy.orm import Session

# from app.models.enf_usr_session import UserSession


# class SessionRepository:

#     def __init__(self, db: Session):
#         self.db = db

#     def save(self, session: UserSession):
#         self.db.add(session)
#         self.db.commit()
#         self.db.refresh(session)
#         return session

#     def find_active_session(self, user_id: str):
#         return (
#             self.db.query(UserSession)
#             .filter(
#                 UserSession.user_id == user_id,
#                 UserSession.is_active == 1
#             )
#             .first()
#         )

#     def find_by_access_jti(self, access_jti: str):
#         return (
#             self.db.query(UserSession)
#             .filter(
#                 UserSession.access_jti == access_jti,
#                 UserSession.is_active == 1
#             )
#             .first()
#         )

#     def find_by_refresh_jti(self, refresh_jti: str):
#         return (
#             self.db.query(UserSession)
#             .filter(
#                 UserSession.refresh_jti == refresh_jti,
#                 UserSession.is_active == 1
#             )
#             .first()
#         )

#     def find_by_user_id(self, user_id: str):
#         return (
#             self.db.query(UserSession)
#             .filter(UserSession.user_id == user_id)
#             .first()
#         )

#     def delete(self, session: UserSession):
#         self.db.delete(session)
#         self.db.commit()

#     def update(self):
#         self.db.commit()





from datetime import datetime

from sqlalchemy.orm import Session

from app.models.enf_usr_session import UserSession


class SessionRepository:

    def __init__(self, db: Session):
        self.db = db

    def save(self, session: UserSession):
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def find_active_session(self, user_id: str):
        return (
            self.db.query(UserSession)
            .filter(
                UserSession.user_id == user_id,
                UserSession.is_active == 1
            )
            .first()
        )

    def find_by_access_jti(self, access_jti: str):
        return (
            self.db.query(UserSession)
            .filter(
                UserSession.access_jti == access_jti,
                UserSession.is_active == 1
            )
            .first()
        )

    def find_by_refresh_jti(self, refresh_jti: str):
        return (
            self.db.query(UserSession)
            .filter(
                UserSession.refresh_jti == refresh_jti,
                UserSession.is_active == 1
            )
            .first()
        )

    def deactivate(self, session: UserSession):
        session.is_active = 0
        session.logout_time = datetime.utcnow()

        self.db.commit()

    def update(self, session: UserSession):
        self.db.commit()
        self.db.refresh(session)
        return session