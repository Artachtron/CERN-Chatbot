from backend.rag.parse import partition_file, sort_elements
from backend.utils.path import PATH
from backend.rag.preprocess import get_table_summary, get_image_summary
from backend.rag.model import Model
from pathlib import Path
import time
from typing import Iterable


def data_from_file(filename: str) -> dict[str, Iterable]:
    filepath = PATH.resources / filename

    elements, temp_folder = partition_file(filepath)
    sorted_elements = sort_elements(elements)

    images = Path(temp_folder.name).iterdir()
    tables = sorted_elements["Table"]
    texts = sorted_elements["CompositeElement"]

    I2T_MODEL = "Salesforce/blip-image-captioning-base"
    T2T_MODEL = "HuggingFaceH4/zephyr-7b-beta"

    I2T_model = Model(I2T_MODEL)
    T2T_model = Model(T2T_MODEL)

    image_summaries = (get_image_summary(I2T_model, image) for image in images)
    tables_summaries = (get_table_summary(T2T_model, table.text) for table in tables)

    temp_folder.cleanup()

    return {
        "original": {"images": images, "tables": tables, "texts": texts},
        "processed": {
            "image_summaries": image_summaries,
            "tables_summaries": tables_summaries,
        },
    }


if __name__ == "__main__":
    start = time.time()
    filename = "CERN-Brochure-2021-007-Eng.pdf"
    data_from_file(filename)
    end = time.time()
    print(f"Time taken: {end-start} seconds")
