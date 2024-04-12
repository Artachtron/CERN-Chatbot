from functools import lru_cache
import weaviate
import weaviate.classes as wvc
from weaviate.classes.config import ReferenceProperty
from backend.utils.conf import CONFIG
from backend.utils.tokens import (
    HF_API_KEY,
    WCS_API_KEY,
    WCS_CLUSTER_URL,
    COHERE_API_KEY,
)


from dataclasses import dataclass, field


@dataclass
class Weaviate:
    embedding_model: str
    wcs_cluster_url: str
    client: weaviate.WeaviateClient = field(init=False)

    def __post_init__(self):
        self.client = self.get_client()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()

    def get_client(self):
        client = weaviate.connect_to_wcs(
            cluster_url=WCS_CLUSTER_URL,
            auth_credentials=weaviate.auth.AuthApiKey(WCS_API_KEY),
            headers={
                "X-HuggingFace-Api-Key": HF_API_KEY,
                "X-Cohere-Api-Key": COHERE_API_KEY,
            },
        )
        return client

    def create_collection(
        self,
        collection_name: str,
        raw: bool = False,
        reference: str = "",
        schema: list[dict] | None = None,
    ):
        schema = schema or []

        vectorizer = (
            wvc.VectorizerConfig(
                text2vec=wvc.Text2VecHuggingface(
                    model=self.embedding_model,
                ),
            )
            if not raw
            else None
        )

        generative = (
            wvc.GenerativeConfig(
                cohere=wvc.CohereConfig(),
            )
            if not raw
            else None
        )

        references = (
            [ReferenceProperty(name=reference, target_collection=reference)]
            if reference
            else []
        )

        self.client.collections.create(
            name=collection_name,
            properties=schema,
            vectorizer_config=vectorizer,
            generative_config=generative,
            references=references,
        )

    def create_reference_and_collection(self, collection_name: str, reference: str):
        self.create_collection(collection_name=reference, raw=True)
        self.create_collection(
            collection_name=collection_name, reference=reference, raw=False
        )

    def get_collection(self, collection_name: str):
        return self.client.collections.get(name=collection_name)

    def add_document(
        self,
        collection_name: str,
        document: dict,
        uuid: str | None = None,
        reference_name: str = "",
        reference_id: str = "",
    ):
        collection = self.get_collection(collection_name)
        collection.data.insert(
            properties=document, uuid=uuid, references={reference_name: reference_id}
        )

    def add_documents(self, collection_name: str, documents: list[dict]):
        collection = self.get_collection(collection_name)
        collection.data.insert_many(objects=documents)

    def add_document_with_reference(
        self,
        collection_name: str,
        document: dict,
        reference: dict,
        reference_collection: str,
        reference_uuid: str,
    ):
        self.add_document(
            collection_name=reference_collection,
            document=reference,
            uuid=reference_uuid,
        )
        self.add_document(
            collection_name=collection_name,
            document=document,
            reference_name=reference_collection,
            reference_id=reference_uuid,
        )


@lru_cache
def get_client():
    return Weaviate(
        embedding_model=CONFIG.embedding_model, wcs_cluster_url=WCS_CLUSTER_URL
    )


if __name__ == "__main__":
    weaviate_client = Weaviate(
        embedding_model=CONFIG.embedding_model, wcs_cluster_url=WCS_CLUSTER_URL
    )
    with weaviate_client as client:
        client.client.collections.delete("CERN")
        client.create_collection("CERN")
        print(client.get_collection("CERN"))
