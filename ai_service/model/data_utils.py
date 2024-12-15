from typing import List

from repository.models import Todo, Task
from common.utils.time_util import format_minutes_to_hours_str
from .user_module import ChecklistItem, UserInfo, FeedbackRequest


def parse_user_info(user_info: dict) -> UserInfo:
    checklist = [
        ChecklistItem(**item) for item in user_info["body"].get("checklist", [])
    ]

    return UserInfo(
        user=user_info["body"]["user"],
        checklist=checklist
    )


def parse_feedback_request_info(feedback_request: dict) -> ChecklistItem:
    checklist = ChecklistItem(**feedback_request.get("checklist", {}))

    return FeedbackRequest(
        duration=feedback_request["duration"],
        checklist=checklist
    )


def make_todo_to_string(todo: Todo, tasks: List[Task]) -> str:
    text_builder = []
    todo_text = f"{todo.id}. {todo.content} (마감일: {todo.deadline})"
    text_builder.append(todo_text)

    task_text_list = []
    for task in tasks:
        task_text_list.append(
            make_task_to_string(task),
        )
    text_builder.extend(task_text_list)

    return "\n".join(text_builder)


def make_task_to_string(task: Task) -> str:
    return f"{task.id}. {task.content} (완료 여부: {'완료' if task.is_completed else '미완료'}, 예상 시간: {format_minutes_to_hours_str(task.expected_duration_minutes)})"
