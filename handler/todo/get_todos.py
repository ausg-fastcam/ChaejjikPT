from repository.todo import list_todos


def get_todos_handler(body, client):
    user_id = body["user"]
    todo_list = list_todos(user_id)
    show_todo_list(client=client, user_id=user_id, todo_list=todo_list)


def show_todo_list(client, user_id, todo_list):
    if not todo_list:
        client.chat_postMessage(
            channel=user_id,
            text="📋 You currently have no TODOs."
        )
    else:
        blocks = []
        for idx, todo in enumerate(todo_list):
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"{idx + 1}. *{todo.content}* (Due: {todo.deadline})"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✔️ Complete"},
                    "value": str(todo.id),
                    "action_id": "complete_todo"
                }
            })

        client.chat_postMessage(
            channel=user_id,
            text="📋 Here are your current TODOs:",
            blocks=blocks
        )
