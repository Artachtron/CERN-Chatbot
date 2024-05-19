from functools import lru_cache
from langchain_community.llms.ollama import Ollama
from config.conf import CONFIG


@lru_cache
def get_model(model: str | None = None, verbose: bool = False):
    model = model or CONFIG.chat_model
    print(f"Using model: {model}")
    ollama = Ollama(
        model=model,
        base_url=CONFIG.ollama_url,
        verbose=verbose,
        num_gpu=2,
        num_thread=12,
    )

    return ollama
