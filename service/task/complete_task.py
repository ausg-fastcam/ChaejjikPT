from datetime import datetime
from repository.task import get_task, update
from repository import SessionLocal
from repository.models import Task


def complete_task(task_id) -> Task | None:
    """
    사용자의 task 목록에서 특정 task를 완료
    """
    task = get_task(task_id)
    task.end_time = datetime.now()
    task.actual_duration_minutes = (task.end_time - task.start_time).min
    return update(task)
