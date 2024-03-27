from backend.rag.template import get_qa_prompt
from backend.rag.model import Model
from backend.utils.conf import CONFIG


def answer_question(question: str, context: str) -> list[dict]:
    model = Model(CONFIG.chat_model)
    prompt = get_qa_prompt(question, context)
    chat_prompt = model.format_prompt(prompt)
    response = model.text_generation(chat_prompt)

    return response
