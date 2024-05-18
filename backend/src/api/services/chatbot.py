from rag.pipeline import answer_question_without_context, get_index, answer_question
from dataclasses import dataclass, field
from llama_index.core import VectorStoreIndex
from rag.model import Model
from config.conf import CONFIG
from functools import lru_cache


@dataclass
class ChatBot:
    filename: str
    index: VectorStoreIndex = field(init=False)
    model: Model = field(init=False)

    def __post_init__(self):
        self.index = get_index(self.filename)
        self.model = Model(CONFIG.chat_model)

    def get_answer(self, question: str):
        return answer_question_without_context(self.model, question)
        return answer_question(self.index, self.model, self.filename, question)


@lru_cache
def get_chatbot(filename: str) -> ChatBot:
    return ChatBot(filename)
