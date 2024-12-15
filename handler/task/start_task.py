from common.constants.constants import START_TASK_ACTION_ID
from handler.resp.task_response import make_todo_task_list_slack_blocks
from repository.task import list_tasks_in_todo
from repository.todo import get_todo
from service.task.start_task import start_task


def register_action_start_task_handler(app):
    @app.action(START_TASK_ACTION_ID)
    def start_task_action_handler(ack, body, client):
        ack()
        user_id = body["user"]["id"]
        task_id = body["actions"][0]["value"]

        started_task = start_task(task_id=task_id)
        if started_task is not None:
            # 새 목록 업데이트
            todo = get_todo(todo_id=started_task.todo_id)
            task_list = list_tasks_in_todo(todo_id=started_task.todo_id)

            updated_blocks = [
                *make_todo_task_list_slack_blocks(todo=todo, task_list=task_list)
            ]

            client.chat_update(
                channel=body["channel"]["id"],
                ts=body["message"]["ts"],
                text="업데이트된 Task 목록입니다.",
                blocks=updated_blocks,
            )

            # 시작 메시지 전송
            client.chat_postMessage(
                channel=user_id,
                text=f"✅ Task Started: {started_task.content}",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"✅ [{started_task.content}] 작업을 시작합니다!"
                        },
                    },
                ]
            )
