from sqlalchemy.orm import Session

from app.models.enf_user import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_email(self, email: str):
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def find_by_user_id(self, user_id: str):
        return (
            self.db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

    def save(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self):
        self.db.commit()

    def delete(self, user: User):
        self.db.delete(user)
        self.db.commit()