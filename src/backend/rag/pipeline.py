import time
import PIL

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
from backend.rag.embedding import get_client
from pathlib import Path

from typing import Iterable
from backend.utils.conf import CONFIG
from backend.databases.postgres.crud import (
    insert_file_content,
    get_file_by_name,
    get_reference,
)

from backend.rag.template import get_qa_prompt
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

    images = {
        f"{filename}_{image.name}": Image(
            name=image.name, path=image, image_bytes=PIL.Image.open(image).tobytes()
        )
        for image in Path(temp_folder.name).iterdir()
    }

    tables = {table.id: table for table in sorted_elements["Table"]}
    texts = {text.id: text for text in sorted_elements["CompositeElement"]}

    I2T_model = Model(CONFIG.image_to_text_model)
    T2T_model = Model(CONFIG.text_to_text_model)

    # image_summaries = {
    #     f"{filename}_{image.name}": get_image_summary(I2T_model, image.path)
    #     for image in images.values()
    # }

    # tables_summaries = {
    #     table.id: get_table_summary(T2T_model, table.text) for table in tables.values()
    # }

    processed_texts = {text.id: text.text for text in texts.values()}

    temp_folder.cleanup()

    return {
        "original": {"images": images, "tables": tables, "texts": texts},
        "processed": {
            # "image_summaries": image_summaries,
            # "tables_summaries": tables_summaries,
            "texts": processed_texts,
        },
    }


def save_file_data(filename: str, data: dict[str, Iterable]) -> None:
    client = get_client()
    with client:
        original_images = data["original"].get("images", {})
        original_tables = data["original"].get("tables", {})
        original_texts = data["original"].get("texts", {})
        processed_images = data["processed"].get("image_summaries", {})
        processed_tables = data["processed"].get("tables_summaries", {})
        processed_texts = data["processed"].get("texts", {})

        collection_name = "CERN"
        reference_name = f"reference_{collection_name}"
        # client.create_reference_and_collection(collection_name, reference_name)

        """ for (image_id, image), processed_image in zip(
            original_images.items(), processed_images.values()
        ):
            client.add_document_with_reference(
                collection_name=collection_name,
                document=image,
                reference=processed_image,
                reference_collection=reference_name,
                reference_uuid=image_id,
            ) """

        for (text_id, text), processed_text in zip(
            original_texts.items(), processed_texts.values()
        ):
            client.add_document_with_reference(
                collection_name=collection_name,
                document={"content": text.text},
                reference={"content": processed_text},
                reference_collection=reference_name,
                reference_id=text_id,
            )


def process_pdf_file(filename):
    data = data_from_file(filename)
    index = save_file_data(filename, data)
    return index


def load_file_data(filename):
    index = load_vectorstore_index(Path(filename).stem)
    return index


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
    start = time.time()
    filename = "CERN-Brochure-2021-007-Eng.pdf"
    process_pdf_file(filename)
    # index = get_index(filename)

    # response = answer_question(index, filename, "What is the LHC?")
    # print(response)

    end = time.time()
    print(f"Time taken: {end-start} seconds")
