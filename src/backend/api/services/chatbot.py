from backend.rag.pipeline import get_index, answer_question
from dataclasses import dataclass, field
from llama_index.core import VectorStoreIndex
from backend.rag.model import Model
from backend.utils.conf import CONFIG


@dataclass
class ChatBot:
    filename: str
    index: VectorStoreIndex = field(init=False)
    model: Model = field(init=False)

    def __post_init__(self):
        self.index = get_index(self.filename)
        self.model = Model(CONFIG.chat_model)

    def get_answer(self, question: str):
        return answer_question(self.index, self.model, self.filename, question)
