from dataclasses import dataclass

from common.constants.constants import VIEW_ADD_TASK_MODAL_ACTION_ID
from repository.models import Task, Todo
from repository.task import create_task
from repository.todo import create_todo, list_todos


@dataclass
class ModalFieldConfig:
    type: str
    action_id: str
    block_id: str


@dataclass
class AddTaskModalConfig:
    task_text: ModalFieldConfig
    due_date: ModalFieldConfig
    expected_duration: ModalFieldConfig  # TODO: 이거 입력하게 할지 말지 결정


add_task_modal_config = AddTaskModalConfig(
    task_text=ModalFieldConfig(
        type="plain_text_input",
        action_id="task_action",
        block_id="task_input"
    ),
    due_date=ModalFieldConfig(
        type="datepicker",
        action_id="date_action",
        block_id="date_input"
    ),
    expected_duration=ModalFieldConfig(
        type="plain_text_input",
        action_id="duration_action",
        block_id="duration_input"
    )
)


def register_view_add_task(app):
    @app.view(VIEW_ADD_TASK_MODAL_ACTION_ID)
    def submit_add_task_modal_handler(ack, body, client):
        # 모달 제출 확인 응답
        ack()

        # 입력값 가져오기
        user_id = body["user"]["id"]
        state_values = body["view"]["state"]["values"]

        # TODO: 좀 더 편하게 입력값을 조회 코드를 사용할 수 있도록 수정
        task_text = state_values[add_task_modal_config.task_text.block_id] \
            [add_task_modal_config.task_text.action_id] \
            ["value"]

        due_date = state_values[add_task_modal_config.due_date.block_id] \
            [add_task_modal_config.due_date.action_id] \
            ["selected_date"]

        expected_duration = state_values[add_task_modal_config.expected_duration.block_id] \
            [add_task_modal_config.expected_duration.action_id] \
            ["value"]

        found_todo = list_todos(user_id)
        todo = found_todo[0] if found_todo else create_todo(
            todo=Todo(user_id=user_id, deadline=due_date, content=task_text))

        created_task = create_task(
            task=Task(todo_id=todo.id, content=task_text, expected_duration_minutes=expected_duration))

        # Slack 메시지로 알림
        client.chat_postMessage(
            channel=user_id,
            text=f"✅ Task Added:\n- Task: {created_task.content}\n- Expected duration: {created_task.expected_duration_minutes}"
        )

    @app.action(VIEW_ADD_TASK_MODAL_ACTION_ID)
    def open_add_task_modal_handler(ack, body, client):
        ack()
        open_add_task_modal(event=body, client=client)


def add_task_handler(event, client):
    show_open_add_task_modal_button(client=client, event=event)


def show_open_add_task_modal_button(client, event):
    client.chat_postMessage(
        channel=event["channel"],
        text="Click the button to open a modal!",
        blocks=[
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "task 추가하기"},
                        "action_id": VIEW_ADD_TASK_MODAL_ACTION_ID
                    }
                ]
            }
        ]
    )


def open_add_task_modal(event, client):
    """
    Add task modal을 열어주는 함수
    *주의 views_open 함수를 사용하기 위해 trigger_id가 필요한데, trigger_id는 app.action인 경우가능함
    따라서 app.aciton으로 들어올 수 있도록 플로우 제어가 필요함

    """
    # TODO: 데이터 모델링에 따라 modal interface 적절하게 수정
    modal_view = {
        "type": "modal",
        "callback_id": VIEW_ADD_TASK_MODAL_ACTION_ID,
        "title": {"type": "plain_text", "text": "Add Task"},
        "submit": {"type": "plain_text", "text": "Add"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": add_task_modal_config.task_text.block_id,
                "label": {"type": "plain_text", "text": "What do you need to do?"},
                "element": {
                    "type": add_task_modal_config.task_text.type,
                    "action_id": add_task_modal_config.task_text.action_id
                },
            },
            {
                "type": "input",
                "block_id": add_task_modal_config.due_date.block_id,
                "label": {"type": "plain_text", "text": "Select a due date"},
                "element": {
                    "type": add_task_modal_config.due_date.type,
                    "action_id": add_task_modal_config.due_date.action_id,
                    "placeholder": {"type": "plain_text", "text": "Select a date"}
                },
            },
            {
                "type": "input",
                "block_id": add_task_modal_config.expected_duration.block_id,
                "label": {"type": "plain_text", "text": "Expected duration (minutes)"},
                "element": {
                    "type": add_task_modal_config.expected_duration.type,
                    "action_id": add_task_modal_config.expected_duration.action_id,
                    "placeholder": {"type": "plain_text", "text": "Enter expected duration"}
                },
            }
        ],
    }

    client.views_open(
        trigger_id=event["trigger_id"],
        view=modal_view,
    )
