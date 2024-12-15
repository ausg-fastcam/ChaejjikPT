from slack_bolt import App

from handler.todo.add_todo import add_todo_handler
from handler.todo.get_todos import get_todos_handler
from handler.task.add_task import add_task_handler
from handler.task.get_tasks import get_tasks_handler
from handler.help import help_handler
from repository.models import User
from repository.user import get_user_by_slack_user_id, create_user
from setting.settings import Settings


def handler_slack_command(say, event, body, client):
    user_id = event["user"]

    text: str = event.get("text", "")
    text = text.replace(f"<@{Settings().SLACK_APP_ID}> ", "").strip()

    user = get_user_by_slack_user_id(slack_user_id=user_id)
    if user is None:
        create_user(user=User(
            slack_user_id=user_id,
            slack_team_id=event["team"],
        ))


    # TODO: 사용자가 입력한 텍스트를 처리하는 로직 정리 필요. LLM에 던지기 등
    if text == "help":
        return help_handler(say=say)
    if text == "add-todo":
        return add_todo_handler(event=event, client=client)
    if text == "get-todos":
        return get_todos_handler(body=event, client=client)
    if text == "add-task":
        return add_task_handler(event=event, client=client)
    if text == "get-tasks":
        return get_tasks_handler(body=event, client=client)
    else:
        return say(f"안녕하세요, <@{user_id}>! 무엇을 도와드릴까요? \n'<@{Settings().SLACK_APP_ID}> help'를 입력해서 원하는 기능을 찾아보세요!")


def register_event_handlers(app: App):
    @app.event("app_mention")
    def handle_app_mentions(event, say, body, client):
        handler_slack_command(say=say, event=event, body=body, client=client)

    @app.event("message")
    def handle_message(event, say, body, client):
        # message 이벤트는 DM 채널일 경우만 동작
        if event.get("channel_type") == "im":
            handler_slack_command(say=say, event=event, body=body, client=client)

        else:
            return
