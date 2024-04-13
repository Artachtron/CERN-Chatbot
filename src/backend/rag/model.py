from huggingface_hub import InferenceClient
from transformers import AutoTokenizer
from backend.utils.tokens import HF_API_KEY, COHERE_API_KEY
from dataclasses import dataclass, field
from backend.utils.path import PATH
import cohere


@dataclass
class Model:
    model_name: str
    model: InferenceClient = field(init=False)
    tokenizer: AutoTokenizer = field(init=False)

    def __post_init__(self):
        self.model = InferenceClient(model=self.model_name, token=HF_API_KEY)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def image_to_text(self, image_path) -> str:
        return self.model.image_to_text(image_path)

    def text_generation(self, prompt: str) -> str:
        return self.model.text_generation(prompt, max_new_tokens=10000)

    def format_prompt(self, prompt: str) -> str:
        return self.tokenizer.apply_chat_template(
            prompt, tokenize=False, add_generation_prompt=True
        )


@dataclass
class Cohere:
    model: cohere.Client = field(init=False)

    def __post_init__(self):
        self.model = cohere.Client(COHERE_API_KEY)

    def format_prompt(self, prompt: str) -> str:
        return prompt

    def text_generation(self, prompt: str) -> str:
        preamble = prompt[0]["content"]
        message = prompt[1]["content"]
        response = self.model.chat(
            preamble=preamble,
            message=message,
        )
        data = response.__dict__
        data["message"] = data.pop("text")
        return data["message"]
