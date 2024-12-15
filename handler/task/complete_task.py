from ai_service.ai_service import generate_feedback
from common.constants.constants import COMPLETE_TASK_ACTION_ID
from handler.resp.task_response import make_todo_task_list_slack_blocks
from repository.task import complete_task, list_tasks_in_todo
from repository.todo import get_todo


def register_action_complete_task_handler(app):
    @app.action(COMPLETE_TASK_ACTION_ID)
    def complete_task_action_handler(ack, body, client):
        ack()
        user_id = body["user"]["id"]
        task_id = body["actions"][0]["value"]
        completed_task = complete_task(task_id=task_id)
        if completed_task is not None:
            # 새 목록 업데이트
            todo_id = completed_task.todo_id

            remained_task_list = list_tasks_in_todo(todo_id=todo_id)
            todo = get_todo(todo_id=todo_id)

            # 삭제 후 메시지 업데이트
            updated_blocks = [
                *make_todo_task_list_slack_blocks(todo=todo, task_list=remained_task_list)
            ]

            client.chat_update(
                channel=body["channel"]["id"],
                ts=body["message"]["ts"],
                text="업데이트된 Task 목록입니다.",
                blocks=updated_blocks,
            )

            generate_feedback_result = generate_feedback(completed_task=completed_task)

            # 잔소리 응답
            client.chat_postMessage(
                channel=user_id,
                text="Task 완료를 축하합니다! 🎉",
                blocks=[
                    {
                        "type": "divider"
                    },
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🎉 [{completed_task.content}] 작업 완료!",
                            "emoji": True
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": generate_feedback_result
                        }
                    }
                ]
            )
