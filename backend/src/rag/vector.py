from contextlib import contextmanager
from typing import Any, Type

import weaviate
from weaviate import WeaviateClient
from weaviate.collections import Collection
import weaviate.classes as wvc
import weaviate.classes.config as wvcc
from rag.schema import Schema, Element
from uuid import UUID
from config.conf import CONFIG
from weaviate.util import generate_uuid5


@contextmanager
def get_local_client():
    try:
        client = weaviate.connect_to_local()
        if not client:
            raise Exception("Weaviate is not running")
        yield client
    finally:
        client.close()


schema_property_map = {
    str: wvcc.DataType.TEXT,
    int: wvcc.DataType.INT,
    float: wvcc.DataType.NUMBER,
    bool: wvcc.DataType.BOOL_ARRAY,
    list[str]: wvcc.DataType.TEXT_ARRAY,
    list[int]: wvcc.DataType.INT_ARRAY,
    list[float]: wvcc.DataType.NUMBER_ARRAY,
    list[bool]: wvcc.DataType.BOOL_ARRAY,
    dict: wvcc.DataType.OBJECT_ARRAY,
    dict[str, str]: wvcc.DataType.OBJECT,
}


def schema2property(schema: Type[Schema]):
    def is_vectorized(field_name: str, schema: Type[Schema]):
        return "__all__" in schema.__vectorized__ or field_name in schema.__vectorized__

    properties = [
        wvcc.Property(
            name=field_name,
            data_type=schema_property_map.get(field_cls, wvcc.DataType.TEXT),
            skip_vectorization=not is_vectorized(field_name, schema),
        )
        for field_name, field_cls in schema.__annotations__.items()
    ]
    return properties


def create_collection(
    client: WeaviateClient,
    collection_name: str,
    schema: Type[Schema],
    skip_vectorization: bool = False,
    delete_if_exists: bool = False,
    references: dict[str, str] | None = None,
) -> Collection:

    if collection_name in client.collections.list_all():
        if delete_if_exists:
            client.collections.delete(collection_name)
        else:
            return client.collections.get(collection_name)

    references = references or {}
    reference_properties = []
    for ref_name, target_collection in references.items():
        reference_properties.append(
            wvcc.ReferenceProperty(name=ref_name, target_collection=target_collection)
        )

    properties = schema2property(schema)

    vectorizer = (
        None
        if skip_vectorization
        else wvcc.Configure.Vectorizer.text2vec_transformers(
            inference_url=CONFIG.inference_url
        )
    )

    return client.collections.create(
        name=collection_name,
        properties=properties,
        vectorizer_config=vectorizer,
        generative_config=wvcc.Configure.Generative.cohere(),
        references=reference_properties,
    )


def create_vectorized_collection(
    client: WeaviateClient,
    collection_name: str,
    schema: Type[Schema],
    delete_if_exists: bool = False,
    references: dict[str, str] | None = None,
) -> Collection:
    return create_collection(
        client,
        collection_name,
        schema,
        skip_vectorization=False,
        delete_if_exists=delete_if_exists,
        references=references,
    )


def create_raw_collection(
    client: WeaviateClient,
    collection_name: str,
    schema: Type[Schema],
    delete_if_exists: bool = False,
    references: dict[str, str] | None = None,
) -> Collection:
    return create_collection(
        client,
        collection_name,
        schema,
        skip_vectorization=True,
        delete_if_exists=delete_if_exists,
        references=references,
    )


def create_reference_and_collection(
    client: WeaviateClient, collection_name: str, reference_name: str
):
    create_raw_collection(
        client, schema=Element, collection_name=reference_name, delete_if_exists=True
    )

    create_vectorized_collection(
        client=client,
        schema=Element,
        collection_name=collection_name,
        references={"from": reference_name},
        delete_if_exists=True,
    )


def add_document(
    client: WeaviateClient,
    collection_name: str,
    document: dict | Schema,
    references: dict[str, UUID] | None = None,
) -> UUID:
    if isinstance(document, Schema):
        document = document.model_dump()

    references = references or {}

    collection = client.collections.get(collection_name)
    return collection.data.insert(
        document, references=references, uuid=generate_uuid5(document)
    )


def add_doc_with_ref(
    client, collection_name: str, reference_name: str, reference: dict, document: dict
):
    reference_id = add_document(
        client,
        collection_name=reference_name,
        document=reference,
        references=None,
    )

    add_document(
        client,
        collection_name=collection_name,
        document=document,
        references={"from": reference_id},
    )


def add_documents(
    client: WeaviateClient,
    collection_name: str,
    documents: list[dict[str, Any] | Schema],
    references: dict[str, UUID] | None = None,
    batch_size: int = 100,
):

    collection = client.collections.get(collection_name)

    with collection.batch.fixed_size(batch_size) as batch:
        for document in documents:
            properties = (
                document.model_dump() if isinstance(document, Schema) else document
            )
            # obj = wvc.data.DataObject(properties=properties, references=references)
            batch.add_object(properties=properties, references=references)
