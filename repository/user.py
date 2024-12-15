from repository import SessionLocal
from repository.models import User


def get_user_by_slack_user_id(slack_user_id: str) -> User | None:
    """
    사용자 정보 조회
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.slack_user_id == slack_user_id).first()
        return user
    finally:
        session.close()


def create_user(user: User) -> User:
    """
    사용자 정보 생성
    """
    session = SessionLocal()
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()
