from pydantic import BaseModel


class Question(BaseModel):
    question: str


class QuestionRequest(BaseModel):
    question: str
    history: list
