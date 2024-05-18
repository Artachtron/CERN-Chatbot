# from unstructured.partition.auto import partition_pdf
from functools import lru_cache
from typing import Any
from unstructured.documents.elements import Element
from unstructured_client import UnstructuredClient
from utils.path import PATH
from pathlib import Path
from config.conf import CONFIG
from utils.tokens import UNSTRUCTURED_API_KEY
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError
from unstructured.partition.api import partition_via_api
import json

# docker run -dt --name unstructured -p 5000:5000 --rm -e PORT=5000 -v C:/Users/flore/Documents/code/CERN-RAG/backend/resources:/app/resources downloads.unstructured.io/unstructured-io/unstructured:latest


@lru_cache
def get_unstructured_client():
    return UnstructuredClient(
        api_key_auth=UNSTRUCTURED_API_KEY,
        server=CONFIG.unstructured_local_url,
        server_url=CONFIG.unstructured_local_url,
    )


def partition_file(file_path: Path):

    output_file: Path = PATH.output / filepath.stem / "elements.json"
    if Path.exists(output_file):
        print(f"Loading {output_file}")
        with open(output_file, "r", encoding="utf-8") as f:
            elements = json.load(f)
            return elements

    client = get_unstructured_client()
    print(f"Processing {file_path}")

    file = open(file_path, "rb")

    req = shared.PartitionParameters(
        files=shared.Files(
            content=file.read(),
            file_name=str(file_path),
        ),
        strategy="fast",
        chunking_strategy="by_title",
        pdf_infer_table_structure=True,
        languages=["eng"],
    )

    elements = []
    try:
        res = client.general.partition(req)
        elements = res.elements
    except SDKError as e:
        print(e)

    # elements = partition_pdf(
    #     filename=file_path,
    #     languages=["en"],
    #     extract_images_in_pdf=True,
    #     extract_image_block_output_dir=temp_folder.name,
    #     chunking_strategy="by_title",
    # )

    if elements:
        save_elements(output_file, elements)

    return elements


def save_elements(output_file: Path, elements: list[Any]):
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(elements, f, indent=2)


def sort_elements(elements: list[Element]) -> dict[str, list[Element]]:
    sorted_elements = {}
    for el in elements:
        category = el.category
        if category not in sorted_elements:
            sorted_elements[category] = []
        sorted_elements[category].append(el)

    return sorted_elements


if __name__ == "__main__":
    # elements, temp_folder = partition_file(PATH.resources / filename)

    filename = "CERN-Brochure-2021-007-Eng.pdf"
    filepath = PATH.resources / filename

    elements = partition_file(filepath)

    # api_url = CONFIG.unstructured_local_url
    """ elements = partition_via_api(
        filename=str(filepath),
        api_url=api_url,
    ) """

    """ client = UnstructuredClient(
        api_key_auth=UNSTRUCTURED_API_KEY,
        server=CONFIG.unstructured_local_url,
        server_url=CONFIG.unstructured_local_url,
    )

    file = open(filepath, "rb")

    req = shared.PartitionParameters(
        files=shared.Files(
            content=file.read(),
            file_name=filename,
        ),
        strategy="fast",
    )

    try:
        res = client.general.partition(req)
        print(res.elements[0])
        elements = res.elements
    except SDKError as e:
        print(e) """

    #
    print(elements)
    print(json.dumps(elements[:], indent=2))
    # sorted_elements = sort_elements(elements)
    # print(sorted_elements)
    # temp_folder.cleanup()
