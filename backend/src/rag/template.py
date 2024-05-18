from langchain_core.prompts import PromptTemplate, PipelinePromptTemplate
from utils.path import PATH
from config.conf import CONFIG


def get_template(template_name: str) -> PromptTemplate:
    with open(PATH.prompts / template_name, "r") as f:
        template = f.read()

    return PromptTemplate.from_template(template)


def get_prompt(
    context_name: str,
    context: str,
    preamble: str,
    query: str,
    query_name: str = "QUERY",
) -> list[dict]:
    separator = "=" * 20
    user_prompt = f"{query_name}: {query}\n{separator}\{context_name.upper()}: {context}\n{separator}\n"
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


# def get_qa_prompt(question: str, context: str) -> list[dict]:
#     preamble = """You are an assistant tasked with answering questions. Use the context provided, just answer the question straight up."""
#     messages = get_prompt("CONTEXT", context, preamble, question, query_name="QUESTION")

#     return messages


def get_qa_template(model_name: str = CONFIG.chat_model) -> PipelinePromptTemplate:
    model_template = get_template(f"{model_name.replace(':','_')}.txt")
    prompt_template = get_template("qa.txt")

    pipeline_prompts = [
        ("prompt", prompt_template),
    ]

    return PipelinePromptTemplate(
        pipeline_prompts=pipeline_prompts,
        final_prompt=model_template,
    )
