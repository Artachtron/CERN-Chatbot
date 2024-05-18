# from unstructured.partition.auto import partition_pdf
from unstructured.documents.elements import Element
from unstructured_client import UnstructuredClient
from utils.path import PATH
from pathlib import Path
from config.conf import CONFIG
from utils.tokens import UNSTRUCTURED_API_KEY
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError
from unstructured.partition.api import partition_via_api

# docker run -dt --name unstructured -p 5000:5000 --rm -e PORT=5000 -v C:/Users/flore/Documents/code/CERN-RAG/backend/resources:/app/resources downloads.unstructured.io/unstructured-io/unstructured:latest


def partition_file(file_path: Path):
    filename = file_path.stem
    print(f"Processing {filename}")
    temp_folder = PATH.create_temp_folder()

    elements = partition_pdf(
        filename=file_path,
        languages=["en"],
        extract_images_in_pdf=True,
        extract_image_block_output_dir=temp_folder.name,
        chunking_strategy="by_title",
    )
    return elements, temp_folder


def sort_elements(elements: list[Element]) -> dict[str, list[Element]]:
    sorted_elements = {}
    for el in elements:
        category = el.category
        if category not in sorted_elements:
            sorted_elements[category] = []
        sorted_elements[category].append(el)

    return sorted_elements


if __name__ == "__main__":
    import json

    # elements, temp_folder = partition_file(PATH.resources / filename)

    filename = "CERN-Brochure-2021-007-Eng.pdf"
    filepath = PATH.resources / filename
    api_url = CONFIG.unstructured_local_url

    """ elements = partition_via_api(
        filename=str(filepath),
        api_url=api_url,
    ) """

    client = UnstructuredClient(
        api_key_auth=UNSTRUCTURED_API_KEY,
        server=CONFIG.unstructured_local_url,
        server_url=CONFIG.unstructured_local_url,
    )

    file = open(filepath, "rb")
    print(filepath)
    req = shared.PartitionParameters(
        # Note that this currently only supports a single file
        files=shared.Files(
            content=file.read(),
            file_name=filename,
        ),
        # Other partition params
        strategy="fast",
    )
    print(filepath)
    try:
        res = client.general.partition(req)
        print(res.elements[0])
        elements = res.elements
    except SDKError as e:
        print(e)

    # element_dict = [el.to_dict() for el in elements]
    print(json.dumps(elements[:], indent=2))
    sorted_elements = sort_elements(elements)
    print(sorted_elements)
    # temp_folder.cleanup()
