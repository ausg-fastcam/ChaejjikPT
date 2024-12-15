import json
from typing import List

from common.constants.constants import COMPLETE_TASK_ACTION_ID, DELETE_TASK_ACTION_ID, \
    START_TASK_ACTION_ID, \
    VIEW_EDIT_TASK_ACTION_ID
from common.utils.time_util import format_minutes_to_hours_str
from repository.models import Task, Todo


def make_todo_slack_text(todo: Todo):
    return f"📋 ({todo.content}) 할일 목록"


def make_todo_task_list_slack_blocks(todo: Todo, task_list: List[Task]) -> list[dict]:
    return [
        todo_header_block(todo=todo),
        {
            "type": "divider"
        },
        *make_task_list_response_slack_blocks(todo_id=todo.id, task_list=task_list),
        {
            "type": "divider"
        },
    ]


def todo_header_block(todo: Todo):
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"📝 {todo.content} (마감: {todo.deadline.strftime('%Y-%m-%d')})",
            "emoji": True
        }
    }


def make_task_list_response_slack_blocks(todo_id, task_list: List[Task]):
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"📌 작업 총 {len(task_list)}개"
                    f"\n📌 총 예상 작업 시간 {format_minutes_to_hours_str(sum([task.expected_duration_minutes for task in task_list]))}"
                )
            }
        },
        {
            "type": "divider",
        }
    ]

    for idx, task in enumerate(task_list):
        # Task 내용을 표시하는 섹션 블록
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{idx + 1}. {task.content}* \n(예상 소요 시간: {format_minutes_to_hours_str(task.expected_duration_minutes)})"
            }
        })

        action_value = json.dumps({"todo_id": todo_id, "task_id": task.id})

        # Complete, Edit, Delete 버튼을 표시하는 Actions 블록
        action_buttons = [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "👊🏻 Start"},
                "value": str(task.id),
                "action_id": START_TASK_ACTION_ID,
            } if not task.start_time else None,
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "✔️ Complete"},
                "style": "primary",
                # TODO: action_value로 변경하고 complete 처리 시 남은 task를 응답하도록
                "value": str(task.id),
                "action_id": COMPLETE_TASK_ACTION_ID,
            } if (task.start_time and not task.end_time) else None,  # 완료된 task는 Complete 버튼을 표시하지 않음
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "✏️ Edit"},
                "value": action_value,
                "action_id": VIEW_EDIT_TASK_ACTION_ID,  # 수정 view modal 열기 액션
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🗑️ Delete"},
                "value": action_value,
                "action_id": DELETE_TASK_ACTION_ID,  # 삭제 요청 액션
            }
        ]

        # 완료된 task의 Complete 버튼은 제외하고 추가
        blocks.append({
            "type": "actions",
            "elements": [button for button in action_buttons if button is not None]
        })

    return blocks
