import weaviate
import json
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from weaviate import EmbeddedOptions
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Document,
    load_index_from_storage,
)
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from backend.utils.conf import CONFIG
from backend.utils.tokens import HF_API_KEY
from backend.utils.path import PATH
from llama_index.core.ingestion import IngestionPipeline


def get_client():
    cls_obj = {
        "class": "CERN",
        "moduleConfig": {
            "text2vec-huggingface": {
                "model": CONFIG.embedding_model,
                "options": {"waitForModel": True, "useGPU": False, "useCache": True},
            }
        },
        "properties": [{"name": "CERN", "dataType": ["text"]}],
        "vectorizer": "text2vec-huggingface",
    }

    client = weaviate.Client(
        embedded_options=EmbeddedOptions(),
        additional_headers={"X-HuggingFace-Api-Key": HF_API_KEY},
    )

    client.schema.delete_all()
    client.schema.create_class(cls_obj)
    print(f"Client is ready: {client.is_ready()}")
    return client


def embed_docs(docs: list[Document], client):
    embedding_model = get_embedding_model()
    with client.batch() as batch:
        batch.size = 5
        for doc in docs:
            vector = embedding_model.get_text_embedding(doc.text)
            properties = {"content": doc.text, "vector": vector, **doc.metadata}
            batch.add_data_object(
                data_object=properties, class_name="CERN", vector=vector
            )


def get_vector_store(client):
    vector_store = WeaviateVectorStore(
        weaviate_client=client, index_name="CERN", text_key="content"
    )

    return vector_store


def get_docstore():
    return SimpleDocumentStore()


def get_storage_context(client):
    docstore = get_docstore()
    vector_store = get_vector_store(client)
    storage_context = StorageContext.from_defaults(
        docstore=docstore, vector_store=vector_store
    )

    return storage_context


def get_embedding_model():
    embedding_model = HuggingFaceEmbedding(model_name=CONFIG.embedding_model)
    return embedding_model


def get_vectorstore_index(
    client, embedding_model, storage_context, docs: list[Document]
):
    index = VectorStoreIndex.from_documents(
        docs,
        embed_model=embedding_model,
        client=client,
        storage_context=storage_context,
        show_progress=True,
    )

    return index


def ingest_documents(docs: list[Document], vector_store, docstore):
    embedding_model = get_embedding_model()

    ingestion_pipeline = IngestionPipeline(
        transformations=[embedding_model],
        docstore=docstore,
        vector_store=vector_store,
    )
    return ingestion_pipeline.run(docs)


def save_vector_store(client, filename: str):
    data = client.data_object.get()

    with open(PATH.documents / filename / "vector_store.jsonl", "w") as f:
        for obj in data["objects"]:
            json.dump(obj, f)
            f.write("\n")


def save_index_storage(index, client, filename: str):
    index.storage_context.persist(
        persist_dir=PATH.documents / filename,
    )

    save_vector_store(client, filename)


def create_vectorstore_index(docs: list[Document], filename: str):
    client = get_client()
    embed_docs(docs, client)

    storage_context = get_storage_context(client)
    # ingest_documents(docs, storage_context.vector_store, storage_context.docstore)

    embedding_model = get_embedding_model()
    index = get_vectorstore_index(client, embedding_model, storage_context, docs)
    save_index_storage(index, client, filename)
    return index


def load_vector_store(client, filename: str):

    with open(PATH.documents / filename / "vector_store.jsonl", "r") as f:
        with client.batch() as batch:
            batch.size = 5
            for line in f:
                obj = json.loads(line)
                batch.add_data_object(data_object=obj["properties"], class_name="CERN")

    return get_vector_store(client)


def load_storage_context(filename: str):
    client = get_client()
    vector_store = load_vector_store(client, filename)
    # vector_store = get_vector_store(client)
    storage_context = StorageContext.from_defaults(
        persist_dir=PATH.documents / filename,
        vector_store=vector_store,
    )
    return storage_context


def load_vectorstore_index(filename: str):
    storage_context = load_storage_context(filename)
    embedding_model = get_embedding_model()
    index = load_index_from_storage(
        storage_context=storage_context, embed_model=embedding_model
    )
    return index
