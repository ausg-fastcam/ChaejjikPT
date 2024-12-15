import json

from common.constants.constants import REVIEW_DIVIDED_TASKS_ACTION_ID
from repository.review_divided_tasks import save_review_divided_tasks, get_review_divided_tasks_by_slack_user_id
from repository.models import ReviewDividedTasks


def register_review_divided_tasks_handler(app):
    @app.action(REVIEW_DIVIDED_TASKS_ACTION_ID)
    def like_divided_tasks_handler(ack, body, client):
        # 액션 확인 응답
        ack()

        # 입력값 가져오기
        user_id = body["user"]["id"]
        actions_value_json = body["actions"][0]["selected_option"]["value"]

        action_value = json.loads(actions_value_json)
        todo_id = action_value["todo_id"]
        score = action_value["score"]

        if get_review_divided_tasks_by_slack_user_id(slack_user_id=user_id) is not None:
            return

        save_review_divided_tasks(review_divided_tasks=ReviewDividedTasks(
            slack_user_id=user_id,
            todo_id=todo_id,
            score=score,
        ))

        client.chat_postMessage(
            channel=user_id,
            text=f"<@{user_id}>님! 소중한 피드백 감사합니다 🙇‍"
        )
