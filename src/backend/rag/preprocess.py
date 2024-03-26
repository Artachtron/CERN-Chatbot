from backend.rag.template import get_table_prompt

def get_table_summary(model, table_text: str) -> str:
    prompt = get_table_prompt(table_text)
    chat_prompt = model.format_prompt(prompt)
    return model.text_generation(chat_prompt)
    
def get_image_summary(model, image_path):
    return model.image_to_text(image_path)