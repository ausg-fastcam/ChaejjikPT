from repository import SessionLocal
from repository.models import ReviewDividedTasks


def get_review_divided_tasks_by_slack_user_id(slack_user_id: str) -> ReviewDividedTasks | None:
    session = SessionLocal()
    try:
        review_divided_tasks = (session.query(ReviewDividedTasks)
                                .filter(ReviewDividedTasks.slack_user_id == slack_user_id)
                                .first())
        return review_divided_tasks
    finally:
        session.close()


def save_review_divided_tasks(review_divided_tasks: ReviewDividedTasks) -> ReviewDividedTasks:
    session = SessionLocal()
    try:
        session.add(review_divided_tasks)
        session.commit()
        session.refresh(review_divided_tasks)
        return review_divided_tasks
    finally:
        session.close()
