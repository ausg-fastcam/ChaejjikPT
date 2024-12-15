from handler.todo.get_todos import show_todo_list
from repository.todo import complete_todo, list_todos


def register_action_complete_todo_handler(app):
    @app.action("complete_todo")
    def complete_todo_action_handler(ack, body, client):
        ack()

        user_id = body["user"]["id"]
        todo_id = body["actions"][0]["value"]
        completed_todo = complete_todo(user_id=user_id, todo_id=todo_id)
        if completed_todo is not None:
            # 완료 메시지 전송
            client.chat_postMessage(
                channel=user_id,
                text=f"✅ Completed TODO: {completed_todo.content} (Due: {completed_todo.deadline})"
            )

            # 새 목록 업데이트
            todo_list = list_todos(user_id)
            show_todo_list(client=client, user_id=user_id, todo_list=todo_list)
