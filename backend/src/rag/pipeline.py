import time
import PIL
import io
import base64
from rag.parse import partition_file, sort_elements
from utils.path import PATH
from rag.preprocess import (
    get_table_summary,
    get_image_summary,
    images2docs,
    tables2docs,
    texts2docs,
)
from rag.model import Model
from rag.embedding import get_client
from pathlib import Path

from typing import Iterable
from utils.conf import CONFIG
from databases.postgres.crud import (
    insert_file_content,
    get_file_by_name,
    get_reference,
)

from rag.template import get_qa_prompt
from dataclasses import dataclass


@dataclass
class Image:
    name: str
    path: str
    image_bytes: bytes


def get_resized_image_bytes(image_path, max_size=(800, 800)):
    # Open the image
    img = PIL.Image.open(image_path)

    # Resize the image
    img.thumbnail(max_size)

    # Convert the image to bytes
    byte_arr = io.BytesIO()
    img.save(byte_arr, format="JPEG")
    return byte_arr.getvalue()


def data_from_file(filename: str) -> dict[str, Iterable]:
    filepath = PATH.resources / filename

    elements, temp_folder = partition_file(filepath)
    sorted_elements = sort_elements(elements)
    I2T_model = Model(CONFIG.image_to_text_model)
    try:
        images = [
            Image(
                name=image.name, path=image, image_bytes=get_resized_image_bytes(image)
            )
            for image in Path(temp_folder.name).iterdir()
        ]

        image_bytes = [
            base64.b64encode(image.image_bytes).decode("utf-8") for image in images
        ]

        image_summaries = [get_image_summary(I2T_model, image.path) for image in images]

    finally:
        temp_folder.cleanup()

    tables = [table.to_dict() for table in sorted_elements["Table"]]
    texts = [text.to_dict() for text in sorted_elements["CompositeElement"]]

    # T2T_model = Model(CONFIG.text_to_text_model)
    T2T_model = Cohere()

    tables_summaries = [get_table_summary(T2T_model, table["text"]) for table in tables]

    processed_texts = [text["text"] for text in texts]
    data = {
        "original": {
            "images": image_bytes,
            "tables": tables,
            "texts": texts,
        },
        "processed": {
            "image_summaries": image_summaries,
            "tables_summaries": tables_summaries,
            "texts": processed_texts,
        },
    }

    return data


import json


def save_file_data(collection_name: str, data: dict[str, Iterable]) -> None:
    with open(PATH.resources / f"{collection_name}.json", "w") as f:
        json.dump(data, f)


def load_file_data(collection_name: str) -> dict[str, Iterable]:
    with open(PATH.resources / f"{collection_name}.json", "r") as f:
        data = json.load(f)
    return data


def store_file_data(collection_name: str, data: dict[str, Iterable]) -> None:
    client = get_client()
    with client:
        original_images = data["original"].get("images", [])
        original_tables = data["original"].get("tables", [])
        original_texts = data["original"].get("texts", [])
        processed_images = data["processed"].get("image_summaries", [])
        processed_tables = data["processed"].get("tables_summaries", [])
        processed_texts = data["processed"].get("texts", [])

        collection_name = collection_name
        reference_name = f"Originals_{collection_name}"
        client.create_reference_and_collection(collection_name, reference_name)

        for image, processed_image in zip(original_images, processed_images):
            client.add_document_with_reference(
                collection_name=collection_name,
                document={"content": processed_image, "type": "image"},
                reference={"content": image, "type": "image"},
                reference_collection=reference_name,
                # reference_id=image_id,
            )

        for table, processed_table in zip(original_tables, processed_tables):
            client.add_document_with_reference(
                collection_name=collection_name,
                document={"content": processed_table, "type": "table"},
                reference={"content": table["text"], "type": "table"},
                reference_collection=reference_name,
                reference_id=table["element_id"],
            )

        for text, processed_text in zip(original_texts, processed_texts):
            client.add_document_with_reference(
                collection_name=collection_name,
                document={"content": processed_text, "type": "text"},
                reference={"content": text["text"], "type": "text"},
                reference_collection=reference_name,
                reference_id=text["element_id"],
            )


def process_pdf_file(filename: str, collection_name: str):
    data = data_from_file(filename)
    save_file_data(collection_name, data)
    # index = save_file_data(collection_name, data)
    # return index


# def load_file_data(filename):
#     index = load_vectorstore_index(Path(filename).stem)
#     return index


def find_context(index, filename: str, question: str) -> str:
    retriever = index.as_retriever()
    context = retriever.retrieve(question)

    full_context = []
    for c in context:
        category = c.metadata["category"]
        reference_id = c.metadata["reference"].replace("-", "")
        reference = get_reference(category, reference_id, filename)
        full_context.append(reference.text)

    return "\n".join(full_context)


def get_index(filename):
    if get_file_by_name(filename) is not None:
        print("File already exists")
        index = load_file_data(filename)

    else:
        index = process_pdf_file(filename)

    return index


def answer_question_from_context(
    model: Model, question: str, context: str
) -> list[dict]:
    prompt = get_qa_prompt(question, context)
    chat_prompt = model.format_prompt(prompt)
    response = model.text_generation(chat_prompt)

    return response


def answer_question(index, model, filename: str, question: str):
    context = find_context(index, filename, question)
    response = answer_question_from_context(model, question, context)
    return response


if __name__ == "__main__":
    import json

    start = time.time()
    filename = "CERN-Brochure-2021-004-Eng.pdf"
    collection_name = "LHC_Brochure_2021"
    # collection_name = "CERN_Quick_Facts_2021"

    # process_pdf_file(filename, collection_name)
    data = load_file_data(collection_name)
    store_file_data(collection_name, data)

    # index = get_index(filename)

    # response = answer_question(index, filename, "What is the LHC?")
    # print(response)

    end = time.time()
    print(f"Time taken: {end-start} seconds")
