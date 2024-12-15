from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from ai_service.ai_service import generate_nagging
from common.constants.constants import NAG_LIMIT_COUNT
from repository.task import list_pending_tasks, list_tasks_in_todo, save_task
from repository.todo import get_todo
from repository.user import get_user_by_slack_user_id


class NaggingScheduler:
    def __init__(self, client, slack_team_id):
        self.__client = client
        self.__slack_team_id = slack_team_id

    def nag_and_update_tasks(self):
        """
        특정 사용자의 잔소리 대상 Task를 조회하고 잔소리 후 업데이트
        """
        tasks = list_pending_tasks()
        for task in tasks:
            todo = get_todo(task.todo_id)
            user = get_user_by_slack_user_id(slack_user_id=todo.user_id)
            if user is None:
                continue

            # 팀이 다른 사용자는 무시
            if user.slack_team_id != self.__slack_team_id:
                continue

            tasks_in_todo = list_tasks_in_todo(todo.id)

            # nag = "🔔 잔소리: " + task.content
            nag = generate_nagging(todo, tasks_in_todo)

            # 잔소리 횟수 증가
            task.nag_count += 1

            # 다음 잔소리 시간 설정
            task.next_nag_time = datetime.now() + timedelta(
                minutes=task.expected_duration_minutes / NAG_LIMIT_COUNT
            )

            save_task(task=task)

            # 잔소리 메시지 전송
            self.__client.chat_postMessage(
                channel=todo.user_id,
                text=nag,
            )

    def schedule_nagging(self):
        # 특정 시간마다 nag_and_update_tasks 호출
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            self.nag_and_update_tasks,
            "interval",
            minutes=1,
            # seconds=10,
        )
        scheduler.start()
