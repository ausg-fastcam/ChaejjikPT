from typing import List, Optional

from pydantic import BaseModel


class ChecklistItem(BaseModel):
    id: int
    task: str
    completed: bool
    due_date: Optional[str]
    priority: Optional[str]


class UserProfile(BaseModel):
    id: int
    name: str
    email: str


class UserInfo(BaseModel):
    user: UserProfile
    checklist: List[ChecklistItem]


class UserInfoRequest(BaseModel):
    success: bool
    message: str
    body: UserInfo


class NaggingMessage(BaseModel):
    nagging: str


class NaggingResponse(BaseModel):
    success: bool
    message: str
    body: NaggingMessage


class FeedbackRequest(BaseModel):
    duration: str
    checklist: ChecklistItem


class FeedbackMessage(BaseModel):
    feedback: str


class FeedbackResponse(BaseModel):
    success: bool
    message: str
    body: FeedbackMessage
