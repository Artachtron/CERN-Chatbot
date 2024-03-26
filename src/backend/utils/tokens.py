from dotenv import load_dotenv
from backend.utils.path import PATH
import os

load_dotenv(PATH.backend / "secrets.env")

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
