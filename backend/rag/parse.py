from unstructured.partition.auto import partition_pdf
from unstructured.documents.elements import Element
from backend.utils.path import PATH
from pathlib import Path


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
