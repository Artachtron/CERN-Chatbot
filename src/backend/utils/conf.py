import yaml
from pydantic import BaseModel
from backend.utils.path import PATH


class Config(BaseModel):
    image_to_text_model: str
    text_to_text_model: str
    chat_model: str
    embedding_model: str


config_path = PATH.config / "config.yaml"

with open(config_path) as config_file:
    CONFIG = Config(**yaml.safe_load(config_file))
