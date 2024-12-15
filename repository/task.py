from datetime import datetime, timedelta

from common.constants.constants import NAG_LIMIT_COUNT
from repository import SessionLocal
from repository.models import Task, Todo


def list_tasks_by_user_id(user_id) -> list[Task]:
    """
    사용자의 모든 task 목록을 반환
    """
    session = SessionLocal()
    try:
        todos = session.query(Todo).filter(Todo.user_id == user_id).all()
        tasks = (session.query(Task)
                 .filter(Task.todo_id.in_([todo.id for todo in todos]))
                 .order_by(Task.id)
                 .all())
        return tasks
    finally:
        session.close()


def list_tasks_in_todo(todo_id) -> list[Task]:
    """
    Todo에 속하는 task 목록을 반환
    """
    session = SessionLocal()
    try:
        tasks = session.query(Task).filter(Task.todo_id == todo_id).order_by(Task.id).all()
        return tasks
    finally:
        session.close()


def list_pending_tasks() -> list[Task]:
    """ TODO: 알림 대상 task 결정 방식 논의
    현재는 유저마다 가장 최근에 시작한 task만을 반환하도록 구현되어 있습니다.
    """
    session = SessionLocal()
    now = datetime.now()
    try:
        now = datetime.now()
        tasks = (
            session.query(Task)
            .distinct(Todo.user_id)
            .join(Todo)
            .filter(
                Task.start_time.isnot(None),
                Task.end_time.is_(None),
            )
            .order_by(Todo.user_id, Task.start_time.desc())
            .all()
        )
        return [task for task in tasks if
                task.next_nag_time is None or task.next_nag_time < now and task.nag_count < NAG_LIMIT_COUNT]
    finally:
        session.close()


def create_tasks(tasks: list[Task]):
    """
    task 목록을 추가
    """
    session = SessionLocal()
    try:
        session.add_all(tasks)
        session.commit()

        # 세션 내에서 데이터 미리 로드
        for task in tasks:
            task.content  # content 속성 접근
            task.expected_duration_minutes  # expected_duration_minutes 속성 접근
    finally:
        session.close()


def create_task(task: Task):
    """
    사용자의 task 목록에 새로운 task를 추가
    """
    session = SessionLocal()
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    finally:
        session.close()


def get_task(task_id) -> Task | None:
    """
    사용자의 task 목록에서 특정 task를 반환
    """

    session = SessionLocal()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        return task
    finally:
        session.close()


def complete_task(task_id) -> Task | None:
    """
    사용자의 task 목록에서 특정 task를 완료
    """
    session = SessionLocal()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            # 영상 제출을 위해 임의로 시간 조정
            completed_time = datetime.now() + timedelta(minutes=task.expected_duration_minutes / 2)

            task.end_time = completed_time
            task.is_completed = True
            task.actual_duration_minutes = (task.end_time - task.start_time).total_seconds() // 60
            session.commit()
            session.refresh(task)
            return task
        return None
    finally:
        session.close()


def delete_task(task_id) -> bool:
    """
    사용자의 task 목록에서 특정 task를 삭제
    """
    session = SessionLocal()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            # delete task
            session.delete(task)
            session.commit()
            return True
        return False
    finally:
        session.close()


def update_task(task_id, content, expected_duration_minutes) -> Task | None:
    """
    사용자의 task 목록에서 특정 task를 수정
    """
    session = SessionLocal()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            task.content = content
            task.expected_duration_minutes = expected_duration_minutes
            session.commit()
            session.refresh(task)
            return task
        return None
    finally:
        session.close()


def save_task(task: Task) -> Task:
    session = SessionLocal()
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    finally:
        session.close()


def update(task: Task) -> Task:
    session = SessionLocal()
    try:
        merged = session.merge(task)
        session.commit()
        session.refresh(merged)
        return merged
    finally:
        session.close()


def update_tasks(tasks: list[Task]):
    """
    Task 목록을 업데이트
    """
    session = SessionLocal()
    try:
        for task in tasks:
            session.merge(task)
        session.commit()
    finally:
        session.close()
