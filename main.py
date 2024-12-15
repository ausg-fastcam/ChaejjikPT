from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from handler.events import register_event_handlers
from handler.task.add_task import register_view_add_task
from handler.task.complete_task import register_action_complete_task_handler
from handler.task.delete_task import register_action_delete_task_handler
from handler.task.edit_task import register_action_edit_task_handler
from handler.task.get_tasks import register_action_get_tasks_handler
from handler.task.review_divided_tasks import register_review_divided_tasks_handler
from handler.task.start_task import register_action_start_task_handler
from handler.todo.add_todo import register_view_add_todo
from handler.todo.complete_todo import register_action_complete_todo_handler
from handler.todo.confirm_create_todo import register_action_confirm_create_todo_handler
from repository import init_db
from service.nagging.scheduler import NaggingScheduler
from setting.settings import Settings
from logger import get_logger

logger = get_logger()

# Slack 앱 초기화
app = App(token=Settings().SLACK_BOT_TOKEN, logger=logger)

# TODO: 대충 정리하기
register_event_handlers(app)
register_view_add_todo(app)
register_action_complete_todo_handler(app)
register_view_add_task(app)
register_action_complete_task_handler(app)
register_action_delete_task_handler(app)
register_action_edit_task_handler(app)
register_action_confirm_create_todo_handler(app)
register_action_start_task_handler(app)
register_action_get_tasks_handler(app)
register_review_divided_tasks_handler(app)

if __name__ == "__main__":
    init_db()
    # 너무 많이 와서 스케쥴러는 잠시 꺼둠
    auth_test_response = app.client.auth_test()
    slack_team_id = auth_test_response["team_id"]
    NaggingScheduler(client=app.client, slack_team_id=slack_team_id).schedule_nagging()
    handler = SocketModeHandler(app, Settings().SLACK_APP_TOKEN)
    handler.start()
