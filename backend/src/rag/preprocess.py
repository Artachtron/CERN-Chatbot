import copy

from rag.template import get_table_prompt


def get_table_summary(model, table_data: dict) -> dict:
    table_data = copy.deepcopy(table_data) or {}
    table_text = table_data["text"]
    prompt = get_table_prompt(table_text)
    chat_prompt = model.format_prompt(prompt)
    summary = model.text_generation(chat_prompt)
    table_data["text"] = summary
    return table_data


def get_image_summary(model, image_path):
    return model.image_to_text(image_path)
