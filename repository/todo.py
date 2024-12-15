import uuid
from typing import List, Dict

from repository import SessionLocal
from repository.models import Todo



def list_todos(user_id) -> List[Todo]:
    """
    사용자의 투두 목록을 반환
    """
    session = SessionLocal()
    try:
        todos = session.query(Todo).filter(Todo.user_id == user_id).all()
        return todos
    finally:
        session.close()


def list_todos_by_ids(todo_ids: List[int]) -> List[Todo]:
    """
    사용자의 투두 목록을 반환
    """
    session = SessionLocal()
    try:
        todos = session.query(Todo).filter(Todo.id.in_(todo_ids)).all()
        return todos
    finally:
        session.close()


def create_todo(todo: Todo) -> Todo:
    """
    사용자의 투두 목록에 새로운 투두를 추가
    """
    session = SessionLocal()
    try:
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo
    finally:
        session.close()


def get_todo(todo_id) -> Todo | None:
    """
    사용자의 투두 목록에서 특정 투두를 반환
    """

    session = SessionLocal()
    try:
        todo = session.query(Todo).filter(Todo.id == todo_id).first()
        return todo
    finally:
        session.close()


def complete_todo(user_id, todo_id) -> Todo | None:
    """
    사용자의 투두 목록에서 특정 투두를 완료
    """
    session = SessionLocal()
    try:
        todo = session.query(Todo).filter(Todo.user_id == user_id, Todo.id == todo_id).first()
        if todo:
            # delete todo
            session.delete(todo)
            session.commit()
            return todo
        return None
    finally:
        session.close()


def delete_todo(user_id, todo_id) -> bool:
    """
    사용자의 투두 목록에서 특정 투두를 삭제
    """
    session = SessionLocal()
    try:
        todo = session.query(Todo).filter(Todo.user_id == user_id, Todo.id == todo_id).first()
        if todo:
            session.delete(todo)
            session.commit()
            return True
        return False
    finally:
        session.close()
