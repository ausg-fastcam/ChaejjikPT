import json

from common.constants.constants import DELETE_TASK_ACTION_ID
from handler.resp.task_response import make_todo_task_list_slack_blocks
from repository.task import delete_task, list_tasks_in_todo
from repository.todo import get_todo


def register_action_delete_task_handler(app):
    @app.action(DELETE_TASK_ACTION_ID)
    def complete_task_action_handler(ack, body, client):
        ack()
        action_value = json.loads(body["actions"][0]["value"])
        todo_id = action_value["todo_id"]
        task_id = action_value["task_id"]

        delete_task(task_id=task_id)

        task_list = list_tasks_in_todo(todo_id=todo_id)
        todo = get_todo(todo_id=todo_id)

        # 삭제 후 메시지 업데이트
        updated_blocks = [
            *make_todo_task_list_slack_blocks(todo=todo, task_list=task_list)
        ]

        client.chat_update(
            channel=body["channel"]["id"],
            ts=body["message"]["ts"],
            text="업데이트된 Task 목록입니다.",  # Blocks의 대체 텍스트
            blocks=updated_blocks,
        )
