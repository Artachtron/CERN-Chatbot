from backend.rag.parse import partition_file, sort_elements
from backend.utils.path import PATH
from backend.rag.preprocess import (
    get_table_summary,
    get_image_summary,
    images2docs,
    tables2docs,
    texts2docs,
)
from backend.rag.model import Model
from backend.rag.embedding import create_vectorstore_index
from pathlib import Path
import time
from typing import Iterable
from backend.utils.conf import CONFIG
from backend.databases.postgres.crud import insert_file_content, get_file_by_name
import PIL

from dataclasses import dataclass


@dataclass
class Image:
    name: str
    path: str
    image_bytes: bytes


def data_from_file(filename: str) -> dict[str, Iterable]:
    filepath = PATH.resources / filename

    elements, temp_folder = partition_file(filepath)
    sorted_elements = sort_elements(elements)

    images = [
        Image(name=image.name, path=image, image_bytes=PIL.Image.open(image).tobytes())
        for image in Path(temp_folder.name).iterdir()
    ]

    tables = sorted_elements["Table"]
    texts = sorted_elements["CompositeElement"]

    I2T_model = Model(CONFIG.image_to_text_model)
    T2T_model = Model(CONFIG.text_to_text_model)

    image_summaries = {
        image.name: get_image_summary(I2T_model, image.path) for image in images
    }
    tables_summaries = {"table_1": "This is a table summary"}
    # tables_summaries = {
    #     table.id: get_table_summary(T2T_model, table.text) for table in tables
    # }

    processed_texts = {text.id: text.text for text in texts}

    temp_folder.cleanup()

    return {
        "original": {"images": images, "tables": tables, "texts": texts},
        "processed": {
            "image_summaries": image_summaries,
            "tables_summaries": tables_summaries,
            "texts": processed_texts,
        },
    }


def save_file_data(filename: str, data: dict[str, Iterable]) -> None:
    original_content = data["original"]
    insert_file_content(filename, original_content)

    # processed_images = data["processed"]["image_summaries"]
    # image_docs = images2docs(processed_images)

    # processed_tables = data["processed"]["tables_summaries"]
    # table_docs = tables2docs(processed_tables)

    # processed_texts = data["processed"]["texts"]
    # text_docs = texts2docs(processed_texts)

    # processed_docs = image_docs + table_docs + text_docs

    # index = create_vectorstore_index(processed_docs)
    # return index


if __name__ == "__main__":
    start = time.time()
    filename = "CERN-Brochure-2021-007-Eng.pdf"
    
    if get_file_by_name(filename) is not None:
        print("File already exists")
    else:
        data = data_from_file(filename)
        index = save_file_data(filename, data)

    end = time.time()
    print(f"Time taken: {end-start} seconds")
