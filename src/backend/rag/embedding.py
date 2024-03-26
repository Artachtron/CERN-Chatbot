import weaviate
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from weaviate import EmbeddedOptions
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from backend.utils.conf import CONFIG
from backend.utils.tokens import HF_API_KEY
from backend.utils.path import PATH


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


def get_storage_context(client):
    docstore = SimpleDocumentStore()
    vector_store = WeaviateVectorStore(
        weaviate_client=client, index_name="CERN", text_key="content"
    )
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
    )

    return index


def save_index_storage(index):
    index.storage_context.persist(
        persist_dir=PATH.documents,
        vector_store_fname="vector_store",
        docstore_fname="docstore",
    )


def create_vectorstore_index(docs: list[Document]):
    client = get_client()
    storage_context = get_storage_context(client)
    embedding_model = get_embedding_model()
    index = get_vectorstore_index(client, embedding_model, storage_context, docs)
    save_index_storage(index)
    return index
