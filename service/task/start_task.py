from datetime import datetime, timedelta
from common.constants.constants import NAG_LIMIT_COUNT
from repository.models import Task
from repository.task import get_task, update


def start_task(task_id) -> Task | None:
    """
    사용자의 task 목록에서 특정 task를 시작
    """
    task = get_task(task_id)
    now = datetime.now()
    task.start_time = now
    task.next_nag_time = now + timedelta(minutes=task.expected_duration_minutes / NAG_LIMIT_COUNT)
    return update(task)
