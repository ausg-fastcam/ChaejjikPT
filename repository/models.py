from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Todo(Base):
    __tablename__ = 'todo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)  # 작업 담당 사용자 ID
    deadline = Column(DateTime, nullable=False)  # 마감일시
    content = Column(String, nullable=False)  # 내용

    # 관계 설정
    tasks = relationship("Task", back_populates="todo", cascade="all, delete")  # 연관된 Todo가 삭제되면 Task도 삭제


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True, autoincrement=True)
    todo_id = Column(Integer, ForeignKey('todo.id'), nullable=False)  # 외래 키
    content = Column(String, nullable=False)  # 내용
    expected_duration_minutes = Column(Integer, nullable=False)  # 기대 소요 시간 (분 단위)
    actual_duration_minutes = Column(Integer, nullable=True)  # 실제 소요 시간 (분 단위)
    is_completed = Column(Boolean, default=False)  # 완료 여부
    start_time = Column(DateTime, nullable=True)  # 시작 일시
    end_time = Column(DateTime, nullable=True)  # 완료 일시
    nag_count = Column(Integer, default=0)  # 잔소리 횟수
    next_nag_time = Column(DateTime, nullable=True)  # 다음 잔소리 시간

    # 관계 설정
    todo = relationship("Todo", back_populates="tasks")


class User(Base):
    __tablename__ = 'users'  # 테이블명은 user 예약어랑 겹쳐서 users로 함
    id = Column(Integer, primary_key=True, autoincrement=True)
    slack_user_id = Column(String, nullable=False, comment="slack user ID")
    slack_team_id = Column(String, nullable=False, comment="slack workspace ID")


class ReviewDividedTasks(Base):
    __tablename__ = 'review_divided_tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    slack_user_id = Column(String, nullable=False)
    todo_id = Column(Integer, nullable=False)
    score = Column(Integer, default=0)


__all__ = ['Base', 'Todo', 'Task', 'User', 'ReviewDividedTasks']
