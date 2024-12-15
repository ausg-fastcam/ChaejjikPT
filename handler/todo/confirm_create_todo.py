import json

from ai_service.ai_service import generate_nagging
from common.constants.constants import CONFIRM_CREATE_TODO_ACTION_ID, GET_TASKS_ACTION_ID
from repository.task import list_tasks_in_todo
from repository.todo import get_todo


def register_action_confirm_create_todo_handler(app):
    @app.action(CONFIRM_CREATE_TODO_ACTION_ID)
    def confirm_create_todo_handler(ack, body, client):
        ack()
        user_id = body["user"]["id"]
        action_value = json.loads(body["actions"][0]["value"])
        todo_id = action_value["todo_id"]

        todo = get_todo(todo_id=todo_id)
        tasks = list_tasks_in_todo(todo_id=todo_id)

        generate_nagging_result = generate_nagging(todo=todo, tasks=tasks)

        client.chat_postMessage(
            channel=user_id,
            text="생성된 잔소리를 확인해보세요.",
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📢 잔소리 알림: 지금 바로 행동하세요!",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🚨 잔소리 시간입니다!*\n\n> _지금부터 할 일을 미루지 말고 즉시 행동하세요._\n"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✨ *생성된 잔소리 목록* ✨\n\n{generate_nagging_result}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "task 조회하기 🔍",
                                "emoji": True
                            },
                            "action_id": GET_TASKS_ACTION_ID,
                            "style": "primary",
                            "value": str(todo_id),
                        },
                        # {
                        #     "type": "button",
                        #     "text": {
                        #         "type": "plain_text",
                        #         "text": "미루기 🙈",
                        #         "emoji": True
                        #     },
                        #     "value": "postpone"
                        # }
                    ]
                }
            ],
        )
