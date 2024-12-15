import json

from common.constants.constants import EDIT_TASK_ACTION_ID, VIEW_EDIT_TASK_ACTION_ID
from handler.resp.task_response import make_todo_task_list_slack_blocks
from repository.task import list_tasks_in_todo, update_task, get_task
from repository.todo import get_todo


def register_action_edit_task_handler(app):
    @app.action(VIEW_EDIT_TASK_ACTION_ID)
    def view_edit_task_action_handler(ack, body, client):
        ack()
        action_value = json.loads(body["actions"][0]["value"])
        todo_id = action_value["todo_id"]
        task_id = action_value["task_id"]
        channel = body["channel"]["id"]
        message_ts = body["message"]["ts"]

        task = get_task(task_id=task_id)

        client.views_open(
            trigger_id=body["trigger_id"],  # 이벤트의 trigger_id
            view={
                "type": "modal",
                "callback_id": EDIT_TASK_ACTION_ID,
                "private_metadata": json.dumps({
                    "todo_id": todo_id,
                    "task_id": task_id,
                    "channel": channel,
                    "message_ts": message_ts,
                }),
                "title": {"type": "plain_text", "text": "Task 수정"},
                "submit": {"type": "plain_text", "text": "수정 완료"},
                "close": {"type": "plain_text", "text": "취소"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "task_content",
                        "label": {"type": "plain_text", "text": "Task 내용"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "content_input",
                            "initial_value": task.content,
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "task_duration",
                        "label": {"type": "plain_text", "text": "예상 소요 시간 (분)"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "duration_input",
                            "initial_value": str(task.expected_duration_minutes),
                        },
                    },
                ],
            },
        )

    @app.view(EDIT_TASK_ACTION_ID)
    def edit_task_action_handler(ack, body, client):
        ack()
        private_metadata = json.loads(body["view"]["private_metadata"])
        todo_id = private_metadata["todo_id"]
        task_id = private_metadata["task_id"]
        channel = private_metadata["channel"]
        message_ts = private_metadata["message_ts"]

        # 사용자 입력 데이터 가져오기
        values = body["view"]["state"]["values"]
        task_content = values["task_content"]["content_input"]["value"]
        task_duration = values["task_duration"]["duration_input"]["value"]

        update_task(task_id=task_id, content=task_content, expected_duration_minutes=task_duration)

        task_list = list_tasks_in_todo(todo_id=todo_id)
        todo = get_todo(todo_id=todo_id)

        # 수정 후 메시지 업데이트
        updated_blocks = [
            *make_todo_task_list_slack_blocks(todo=todo, task_list=task_list)
        ]

        client.chat_update(
            channel=channel,
            ts=message_ts,
            text="업데이트된 Task 목록입니다.",
            blocks=updated_blocks,
        )
