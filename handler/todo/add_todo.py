import json
from dataclasses import dataclass
from typing import List

from ai_service.ai_service import divide_tasks
from ai_service.model.divide_tasks_result import DivideTasksResult
from common.constants.constants import CONFIRM_CREATE_TODO_ACTION_ID, GET_TASKS_ACTION_ID, \
    VIEW_ADD_TODO_MODAL_ACTION_ID, REVIEW_DIVIDED_TASKS_ACTION_ID
from handler.resp.task_response import make_todo_task_list_slack_blocks
from repository.models import Task
from repository.task import create_tasks
from repository.todo import Todo, create_todo, list_todos


@dataclass
class ModalFieldConfig:
    action_id: str
    type: str
    label_text: str
    placeholder_text: str
    block_id: str


@dataclass
class AddTodoModalConfig:
    action_id = VIEW_ADD_TODO_MODAL_ACTION_ID
    description: ModalFieldConfig
    deadline: ModalFieldConfig


add_todo_modal_config = AddTodoModalConfig(
    description=ModalFieldConfig(
        type="plain_text_input",
        label_text="어떤 일을 해야하는지 설명해주세요. 자세하게 설명할 수록 task가 잘 나뉘어져요!",
        placeholder_text="할 일을 잘 마무리할 수 있도록 잔소리 해주는 슬렉 봇 개발",
        action_id="todo_action",
        block_id="todo_input"
    ),
    deadline=ModalFieldConfig(
        type="datepicker",
        label_text="데드라인을 설정해주세요",
        placeholder_text="Select a date",
        action_id="date_action",
        block_id="date_input"
    )
)


def register_view_add_todo(app):
    @app.view(VIEW_ADD_TODO_MODAL_ACTION_ID)
    def submit_add_todo_modal_handler(ack, body, client):
        # 모달 제출 확인 응답
        ack()

        # 입력값 가져오기
        user_id = body["user"]["id"]
        state_values = body["view"]["state"]["values"]

        # TODO: 좀 더 편하게 입력값을 조회 코드를 사용할 수 있도록 수정
        description = state_values[add_todo_modal_config.description.block_id] \
            [add_todo_modal_config.description.action_id] \
            ["value"]
        deadline = state_values[add_todo_modal_config.deadline.block_id] \
            [add_todo_modal_config.deadline.action_id] \
            ["selected_date"]

        divide_tasks_result: DivideTasksResult | None = None

        try:
            divide_tasks_result = divide_tasks(task=description, deadline=deadline)
        except Exception as e:
            client.chat_postMessage(
                channel=user_id,
                text=f"{e}"
            )

        # 이론상 해당 조건에 걸릴 수 없지만 혹시 모르니 예외처리
        if divide_tasks_result is None:
            client.chat_postMessage(
                channel=user_id,
                text=f"에러가 발생했습니다. 개발자에게 문의해주세요."
            )

        # TODO: todo, tasks 생성을 transaction으로 묶어야 함
        new_todo = Todo(
            user_id=user_id,
            content=description,
            deadline=deadline,
        )
        create_todo(new_todo)

        tasks: List[Task] = [
            Task(
                todo_id=new_todo.id,
                content=divide_task.description,
                expected_duration_minutes=divide_task.expected_duration_minutes,
            ) for divide_task in divide_tasks_result.tasks
        ]
        create_tasks(tasks)

        client.chat_postMessage(
            channel=user_id,
            text="✅ Task Added:",
            blocks=[
                {
                    "type": "divider"
                },
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📝 작업 분리 완료! 채찍피티가 준비한 작업 가이드를 참고해보세요!",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{divide_tasks_result.guidance}"
                    }
                }
            ]
        )

        # slack update message는 ts를 기준으로하므로 이렇게 메시지를 나눠서 보내야 수정할 때 해당 메시지만 수정할 수 있음
        # task 수정 시에 활용
        client.chat_postMessage(
            channel=user_id,
            text="📋 Here are your current Tasks:",
            blocks=[
                *make_todo_task_list_slack_blocks(todo=new_todo, task_list=tasks),
            ]
        )

        # confirm 버튼 노출
        client.chat_postMessage(
            channel=user_id,
            text="✅ Task Added:",
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📝 TODO 생성 확인",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            "아래 확인 버튼을 눌러서 채찍피티의 좀 더 디테일한 작업 가이드를 확인해보세요!"
                        )
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "확인"},
                            "style": "primary",
                            "action_id": CONFIRM_CREATE_TODO_ACTION_ID,
                            "value": json.dumps({"todo_id": new_todo.id})
                        },
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "생성된 작업이 맘에 드셨나요? 평점을 남겨주세요!"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "점수 선택",
                                "emoji": True
                            },
                            "options": [
                                {"text": {"type": "plain_text", "text": "1점"},
                                 "value": json.dumps({"todo_id": new_todo.id, "score": 1})},
                                {"text": {"type": "plain_text", "text": "2점"},
                                 "value": json.dumps({"todo_id": new_todo.id, "score": 2})},
                                {"text": {"type": "plain_text", "text": "3점"},
                                 "value": json.dumps({"todo_id": new_todo.id, "score": 3})},
                                {"text": {"type": "plain_text", "text": "4점"},
                                 "value": json.dumps({"todo_id": new_todo.id, "score": 4})},
                                {"text": {"type": "plain_text", "text": "5점"},
                                 "value": json.dumps({"todo_id": new_todo.id, "score": 5})},
                            ],
                            "action_id": REVIEW_DIVIDED_TASKS_ACTION_ID
                        }
                    ]
                }
            ]
        )

    @app.action(VIEW_ADD_TODO_MODAL_ACTION_ID)
    def open_add_todo_modal_handler(ack, body, client):
        ack()
        open_add_todo_modal(event=body, client=client)


def add_todo_handler(event, client):
    # 현재는 todo 하나만 지원하도록 구현
    user_id = event["user"]
    todo_list = list_todos(user_id=user_id)
    channel_id = event["channel"]

    guide_text_for_non_dm_channel = "*참고: 생성된 Task 목록은 DM에서 확인할 수 있습니다."

    if len(todo_list) > 0:
        slack_blocks = [
            {
                "type": "divider"
            },
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📝 이미 생성된 TODO가 있습니다. 확인하시겠습니까?",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": guide_text_for_non_dm_channel,
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "TODO 확인하기"},
                        "style": "primary",
                        "value": str(todo_list[0].id),
                        "action_id": GET_TASKS_ACTION_ID
                    }
                ]
            },
            {
                "type": "divider"
            },
        ]

        return client.chat_postMessage(
            channel=channel_id,
            text="이미 생성된 TODO가 있습니다. 확인하시겠습니까?",
            blocks=slack_blocks
        )

    client.chat_postMessage(
        channel=channel_id,
        text="Click the button to open a modal!",
        blocks=[
            {
                "type": "divider"
            },
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📝 Todo 추가하기 버튼을 클릭해서 Todo를 추가해보세요!",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "Todo를 추가하면 입력한 내용에 따라 자동으로 Task가 생성됩니다."
                        f"\n{guide_text_for_non_dm_channel}"
                    ),
                }
            },
            make_open_add_todo_modal_button_slack_block(),
            {
                "type": "divider"
            },
        ]
    )


def make_open_add_todo_modal_button_slack_block():
    return {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Todo 추가하기"},
                "style": "primary",
                "action_id": VIEW_ADD_TODO_MODAL_ACTION_ID
            }
        ]
    }


def open_add_todo_modal(event, client):
    """
    Add todo modal을 열어주는 함수
    *주의 views_open 함수를 사용하기 위해 trigger_id가 필요한데, trigger_id는 app.action인 경우가능함
    따라서 app.aciton으로 들어올 수 있도록 플로우 제어가 필요함

    """

    # TODO: 데이터 모델링에 따라 modal interface 적절하게 수정
    modal_view = {
        "type": "modal",
        "callback_id": VIEW_ADD_TODO_MODAL_ACTION_ID,
        "title": {"type": "plain_text", "text": "Todo 추가하기"},
        "submit": {"type": "plain_text", "text": "Add"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": add_todo_modal_config.description.block_id,
                "label": {"type": "plain_text", "text": add_todo_modal_config.description.label_text},
                "element": {
                    "type": add_todo_modal_config.description.type,
                    "action_id": add_todo_modal_config.description.action_id,
                    "placeholder": {"type": "plain_text", "text": add_todo_modal_config.description.placeholder_text}
                },
            },
            {
                "type": "input",
                "block_id": add_todo_modal_config.deadline.block_id,
                "label": {"type": "plain_text", "text": add_todo_modal_config.deadline.label_text},
                "element": {
                    "type": add_todo_modal_config.deadline.type,
                    "action_id": add_todo_modal_config.deadline.action_id,
                    "placeholder": {"type": "plain_text", "text": add_todo_modal_config.deadline.placeholder_text}
                },
            }
        ],
    }

    client.views_open(
        trigger_id=event["trigger_id"],
        view=modal_view,
    )
