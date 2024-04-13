from functools import lru_cache
import weaviate
import weaviate.classes as wvc
import time

from weaviate.classes.config import ReferenceProperty, Property
from weaviate.classes.config import Configure
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

    # def __post_init__(self):
    # self.client = self.get_client()

    def __enter__(self):
        self.client = self.get_client()
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
        reference_name: str = "",
        schema: list[dict] | None = None,
    ):
        schema = schema or []

        vectorizer = (
            Configure.Vectorizer.text2vec_huggingface(model=self.embedding_model)
            if not raw
            else None
        )

        generative = Configure.Generative.cohere() if not raw else None

        references = (
            [
                # ReferenceProperty(name=reference_name, target_collection=reference_name)
            ]
            if reference_name
            else []
        )

        """ if reference_name:
            ref_prop = Property(
                name=self._format_reference(reference_name),
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,
                vectorize_property_name=False,
            )
            schema.append(ref_prop) """

        self.client.collections.create(
            name=collection_name,
            properties=schema,
            vectorizer_config=vectorizer,
            generative_config=generative,
            references=references,
        )

    def create_reference_and_collection(
        self, collection_name: str, reference_name: str
    ):
        existing_collections = self.client.collections.list_all()
        if not reference_name in existing_collections:
            self.create_collection(collection_name=reference_name, raw=True)
        
        else:
            print(f"Collection {reference_name} already exists")

        if not collection_name in existing_collections:
            self.create_collection(
                collection_name=collection_name, reference_name=reference_name, raw=False
            )
        else:
            print(f"Collection {collection_name} already exists")

    def get_collection(self, collection_name: str):
        return self.client.collections.get(name=collection_name)

    def add_document(
        self,
        collection_name: str,
        document: dict,
        uuid: str | None = None,
        reference_name: str = "",
        reference_id: str = "",
        retries: int = 5,
        delay: int = 5,
    ):
        references = {reference_name: reference_id} if reference_name else {}
        references = {}

        if reference_name:
            document[reference_name] = reference_id

        collection = self.get_collection(collection_name)
        for i in range(retries):
            try:
                return collection.data.insert(
                    properties=document, uuid=uuid, references=references
                )
            except weaviate.exceptions.UnexpectedStatusCodeError as e:
                if i < retries - 1:  # i is zero indexed
                    time.sleep(delay)  # wait before trying again
                else:
                    raise e

    def _create_reference(self, reference_name: str, reference_id):
        return {self._format_reference(reference_name): reference_id}

    def _format_reference(self, reference_name: str) -> str:
        return f"{reference_name}"

    def get_reference(self, obj, reference_name: str):
        property_name = reference_name[0].lower() + reference_name[1:]
        uuid = obj.properties.get(property_name)
 
        return self._get_reference(reference_name, uuid)

    def _get_reference(self, reference_name: str, reference_id: str):
        reference_collection = self.get_collection(reference_name)
        objects ={obj.uuid: obj for obj in reference_collection.iterator()}
        for uuid, obj in objects.items():
            if uuid == reference_id:
                return obj
    
    def add_documents(self, collection_name: str, documents: list[dict]):
        collection = self.get_collection(collection_name)
        collection.data.insert_many(objects=documents)

    def add_document_with_reference(
        self,
        collection_name: str,
        document: dict,
        reference: dict,
        reference_collection: str,
        reference_id: str | None = None,
    ):
        reference_uuid = self.add_document(
            collection_name=reference_collection,
            document=reference,
            uuid=reference_id,
        )

        self.add_document(
            collection_name=collection_name,
            document=document,
            reference_name=reference_collection,
            reference_id=reference_uuid,
        )
        
    def query_reference_context(self, collection_name: str, query: str, reference_name: str, top_k: int = 1):
        collection = self.get_collection(collection_name)
        result = collection.query.near_text(query, limit=top_k)
         
        return [self.get_reference(obj, reference_name).properties for obj in result.objects]


@lru_cache
def get_client():
    return Weaviate(
        embedding_model=CONFIG.embedding_model, wcs_cluster_url=WCS_CLUSTER_URL
    )


if __name__ == "__main__":

    weaviate_client = Weaviate(
        embedding_model=CONFIG.embedding_model, wcs_cluster_url=WCS_CLUSTER_URL
    )
    # Define constants
    COLLECTION_NAME_CERN = "CERN"
    COLLECTION_NAME_REFERENCE_CERN = "reference_CERN"
    PROPERTY_NAME_TEXT = "text"
    PROPERTY_DATA_TYPE_TEXT = wvc.config.DataType.TEXT
    REFERENCE_NAME_ORIGINAL_DOC = "original_doc"
    REFERENCE_TEXT = "some reference text"
    DOCUMENT_TEXT = "some text"

    with weaviate_client as client:
        """ client.client.collections.delete(COLLECTION_NAME_CERN)
        client.client.collections.delete(COLLECTION_NAME_REFERENCE_CERN)
        client.client.collections.create(
            COLLECTION_NAME_REFERENCE_CERN,
            properties=[
                wvc.config.Property(
                    name=PROPERTY_NAME_TEXT, data_type=PROPERTY_DATA_TYPE_TEXT
                )
            ],
        )
        reference_collection = client.get_collection(COLLECTION_NAME_REFERENCE_CERN)

        reference = {PROPERTY_NAME_TEXT: REFERENCE_TEXT}
        uuid = reference_collection.data.insert(properties=reference)
        print(reference_collection.query.fetch_object_by_id(uuid=uuid))
        client.client.collections.create(
            COLLECTION_NAME_CERN,
            # vectorizer_config=Configure.Vectorizer.text2vec_huggingface(
            #     model=client.embedding_model
            # ),
            properties=[
                wvc.config.Property(
                    name=PROPERTY_NAME_TEXT, data_type=PROPERTY_DATA_TYPE_TEXT
                )
            ],
            references=[
                wvc.config.ReferenceProperty(
                    name=REFERENCE_NAME_ORIGINAL_DOC,
                    target_collection=COLLECTION_NAME_REFERENCE_CERN,
                )
            ],
        )

        cern_collection = client.get_collection(COLLECTION_NAME_CERN)
        print(
            cern_collection.config._get_reference_by_name(REFERENCE_NAME_ORIGINAL_DOC)
        )

        document = {PROPERTY_NAME_TEXT: DOCUMENT_TEXT}
        obj_uuid = cern_collection.data.insert(
            properties=document,
            references={REFERENCE_NAME_ORIGINAL_DOC: uuid},
        )

        client.client.data_object.reference.add(
            from_uuid=obj_uuid,
            from_property_name=REFERENCE_NAME_ORIGINAL_DOC,
            to_uuid=uuid,
            from_class_name=COLLECTION_NAME_CERN,
            to_class_name=COLLECTION_NAME_REFERENCE_CERN,
        ) """

        """ ref = wvc.data.DataReference(
            from_uuid=obj_uuid,
            from_property="original_doc",
            to_uuid=uuid,
        )
        cern_collection.data.reference_add(
            from_uuid=obj_uuid,
            from_property="original_doc",
            to=uuid,
        ) """
        # print(cern_collection.query.fetch_object_by_id(uuid=obj_uuid))
        # client.create_reference_and_collection("CERN", "reference_CERN")

        # cern_collection = client.get_collection("CERN")
        # reference_collection = client.get_collection("reference_CERN")
        # print(cern_collection)

        # document = {"text": "some text"}
        #
        # test = reference_collection.data.insert(properties=reference)
        # cern_collection.data.insert(
        #     properties=document,
        #     references={"reference_CERN": "uuid"},
        # )
        # print(test)

        # client.add_document("CERN", document)

        # print(len(cern_collection))
        # all_objects = cern_collection.iterator()

        """ client.client.collections.delete(COLLECTION_NAME_CERN)
        client.client.collections.delete(COLLECTION_NAME_REFERENCE_CERN) """
        
        # client.create_reference_and_collection(
        #     COLLECTION_NAME_CERN, COLLECTION_NAME_REFERENCE_CERN
        # )

        # client.client.collections.delete_all()
        # cern_collection = client.get_collection(COLLECTION_NAME_CERN)
        # reference_collection = client.get_collection(COLLECTION_NAME_REFERENCE_CERN)
        
        # print(cern_collection)
        
        # document = {"text": "some text"}
        # reference = {"text": "some reference text"}
        
        # client.add_document_with_reference(
        #     collection_name=COLLECTION_NAME_CERN,
        #     document=document,
        #     reference=reference,
        #     reference_collection=COLLECTION_NAME_REFERENCE_CERN,
        #     # reference_id="uuid",
        # )

        # result = cern_collection.query.near_text("text")
        # for obj in result.objects[:1]:
        #     reference = client.get_reference(obj, COLLECTION_NAME_REFERENCE_CERN)
            # print(reference.properties)
            
        

        # reference_collection.data.insert(properties=reference)
        # cern_collection.data.insert(properties=document,
        #                             # references={"reference_CERN": "uuid"}
        #                             )

        # for obj in reference_collection.iterator():
        #     print(obj)
        # print(client.client.collections.list_all())
        # client.client.collections.delete_all()
        
        """ for col in client.client.collections.list_all():
            if 'LHC' in col:
                client.client.collections.delete(col) """
        
        print(client.client.collections.list_all().keys())
        
        collection_name = "Quick_Facts_CERN_2021"
        reference_name = f"Originals_{collection_name}"
        cern_collection = client.get_collection(collection_name)
        reference_collection = client.get_collection(reference_name)
        # for obj in cern_collection.iterator():
        #     print(obj.properties['content'])
        #     uuid = (obj.properties.get(COLLECTION_NAME_REFERENCE_CERN))
        #     print(uuid)
            # print(client.get_reference(obj, COLLECTION_NAME_REFERENCE_CERN))
        
        query = "What is the budget of CERN?"
        result = client.query_reference_context(collection_name, query, reference_name, 3)
        separator = "\n"*2 + "=" * 50 + "\n"*2
        context = f"{separator}".join([result['content'] for result in result])
        # print(context)
        # print(len(result))

        # client.client.collections.delete_all()
