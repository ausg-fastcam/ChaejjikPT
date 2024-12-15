from common.constants.constants import GET_TASKS_ACTION_ID
from handler.resp.task_response import make_todo_task_list_slack_blocks
from repository.models import Task, Todo
from repository.task import list_tasks_by_user_id, list_tasks_in_todo
from repository.todo import get_todo, list_todos_by_ids


def register_action_get_tasks_handler(app):
    @app.action(GET_TASKS_ACTION_ID)
    def get_tasks_action_handler(ack, body, client):
        ack()

        user_id = body["user"]["id"]
        todo_id = body["actions"][0]["value"]

        task_list = list_tasks_in_todo(todo_id=todo_id)
        todo = get_todo(todo_id=todo_id)

        client.chat_postMessage(
            channel=user_id,
            text=make_todo_slack_text(todo=todo),
            blocks=make_todo_task_list_slack_blocks(todo=todo, task_list=task_list)
        )


def get_tasks_handler(body, client):
    user_id = body["user"]
    task_list = list_tasks_by_user_id(user_id)
    show_task_list(client=client, user_id=user_id, task_list=task_list)


def show_task_list(client, user_id, task_list: list[Task]):
    if not task_list:
        client.chat_postMessage(
            channel=user_id,
            text="📋 You currently have no Tasks."
        )
    else:
        todo_ids = list(set([task.todo_id for task in task_list]))

        task_list_by_todo_id = {}
        for task in task_list:
            if task.todo_id not in task_list_by_todo_id:
                task_list_by_todo_id[task.todo_id] = []
            task_list_by_todo_id[task.todo_id].append(task)

        todo_list = list_todos_by_ids(todo_ids=todo_ids)

        for todo in todo_list:
            if todo.id not in task_list_by_todo_id:
                continue

            client.chat_postMessage(
                channel=user_id,
                text=make_todo_slack_text(todo=todo),
                blocks=make_todo_task_list_slack_blocks(todo=todo, task_list=task_list_by_todo_id[todo.id])
            )


def make_todo_slack_text(todo: Todo):
    return f"📋 ({todo.content}) 할일 목록"

