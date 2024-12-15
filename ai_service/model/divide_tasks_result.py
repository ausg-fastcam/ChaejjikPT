from typing import List
from pydantic import BaseModel


class DividedTask(BaseModel):
    description: str
    expected_duration_minutes: int


class DivideTasksResult(BaseModel):
    guidance: str
    tasks: List[DividedTask]
