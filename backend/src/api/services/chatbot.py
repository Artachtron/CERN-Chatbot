from rag.pipeline import (
    answer_question,
)
from dataclasses import dataclass, field
from rag.model import Model
from functools import lru_cache
from rag.llm import get_model


@dataclass
class ChatBot:
    filename: str
    model: Model = field(init=False)

    def __post_init__(self):
        self.model = get_model()

    def get_answer(self, question: str, history: list | None = None):
        for chunk in answer_question(question, history=history):
            print(chunk)
            yield chunk


@lru_cache
def get_chatbot(filename: str) -> ChatBot:
    return ChatBot(filename)
