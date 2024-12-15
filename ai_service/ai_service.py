from typing import List

from dotenv import load_dotenv
from openai import OpenAI

from ai_service.model.data_utils import make_todo_to_string, make_task_to_string
from ai_service.model.divide_tasks_result import DivideTasksResult
from ai_service.prompts.base_prompts import DIVIDE_TASK_REQUEST_PROMPT, DIVIDE_TASK_SYSTEM_PROMPT_V2, \
    FEEDBACK_REQUEST_PROMPT, FEEDBACK_SYSTEM_PROMPT, NAGGING_REQUEST_PROMPT, NAGGING_SYSTEM_PROMPT
from common.utils.time_util import format_minutes_to_hours_str
from repository.models import Todo, Task
from setting.settings import Settings

load_dotenv()
openai_api_key = Settings().OPENAI_API_KEY
client = OpenAI(api_key=openai_api_key)


def divide_tasks(task: str, deadline: str) -> DivideTasksResult:
    """
    Generate a json of divided tasks context for the given task info.
    """
    formatted_prompt = DIVIDE_TASK_REQUEST_PROMPT.format(TASK=task, DEADLINE=deadline)

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": DIVIDE_TASK_SYSTEM_PROMPT_V2},
            {"role": "user", "content": formatted_prompt}
        ],
        temperature=1,
        max_tokens=3000,
        response_format=DivideTasksResult
    )

    response_content = response.choices[0].message.content
    return DivideTasksResult.parse_raw(response_content)


def generate_feedback(completed_task: Task) -> str:
    """
    Generate a feedback context for the given task info.
    """

    completed_task_string = make_task_to_string(task=completed_task)

    formatted_prompt = FEEDBACK_REQUEST_PROMPT.format(
        COMPLETED_TASK=completed_task_string,
        EXPECTED_DURATION=format_minutes_to_hours_str(completed_task.expected_duration_minutes),
        ACTUAL_DURATION=format_minutes_to_hours_str(completed_task.actual_duration_minutes),
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": FEEDBACK_SYSTEM_PROMPT},
            {"role": "user", "content": formatted_prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content


def generate_nagging(todo: Todo, tasks: List[Task]) -> str:
    """
    Generate a nagging context for the given user info.
    """

    todo = make_todo_to_string(todo=todo, tasks=tasks)
    formatted_prompt = NAGGING_REQUEST_PROMPT.format(TODO=todo)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": NAGGING_SYSTEM_PROMPT},
            {"role": "user", "content": formatted_prompt}
        ],
        temperature=0.5,
        max_tokens=1000
    )

    # [NOTE] GPT놈이 자꾸 **를 붙여서 markdown 형식으로 반환해서 이를 slack에 잘 보여줄 수 있게 *로 변환함
    response_content = response.choices[0].message.content
    response_content = (
        response_content
        .replace("**", "*")
        .strip()
    )
    return response_content
