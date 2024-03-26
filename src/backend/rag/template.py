
def get_prompt(
    context_name: str, context: str, preamble: str, query: str
) -> list[dict]:
    separator = "=" * 20
    user_prompt = f"QUERY: {query}\n{separator}\{context_name.upper()}: {context}\n{separator}\n"
    messages = [
        {"role": "system", "content": preamble},
        {"role": "user", "content": user_prompt},
    ]

    return messages

def get_table_prompt(table_text: str) -> list[dict]:
    preamble = """You are an assistant tasked with summarizing tables."""
    question = "Give a concise summary of the table."
    messages = get_prompt("TABLE", table_text, preamble, question)

    return messages