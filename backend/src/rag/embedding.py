import logging
import weaviate
import weaviate.classes as wvc
import json
from weaviate.classes.config import ReferenceProperty, Property
from weaviate.classes.config import Configure
from config.conf import CONFIG
from utils.tokens import (
    HF_API_KEY,
    WCS_API_KEY,
    WCS_CLUSTER_URL,
    COHERE_API_KEY,
)
import numpy as np
import uuid


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

def cosine_similarity(vec1, vec2):
    # Compute the dot product of vec1 and vec2
    dot_product = np.dot(vec1, vec2)
    
    # Compute the L2 norms (Euclidean norms) of vec1 and vec2
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    # Compute the cosine similarity
    similarity = dot_product / (norm_vec1 * norm_vec2)
    
    return similarity

def maximal_marginal_relevance(results, k, lambda_param=0.5):

    selected = []
    while results and len(selected) < k:
        if not selected:
            # Select the document with the highest score for the first selection
            selected.append(results.pop(0))
        else:
            # Compute similarities between selected documents and remaining results
            similarities = [[cosine_similarity(obj1.vector['default'], obj2.vector['default']) for obj2 in results] for obj1 in selected]
            max_similarities = np.max(similarities, axis=0)
            
            # Compute MMR scores
            mmr_scores = [(1 - lambda_param) * (-obj.metadata.distance) - lambda_param * max_similarity for (obj, max_similarity) in zip(results, max_similarities)]
            
            # Select the document with the highest MMR score
            selected.append(results.pop(np.argmax(mmr_scores)))
    
    return selected



4



    

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
            collection_name=collection_name,
            reference_name=reference_name,
            raw=False,
        )
    else:
        print(f"Collection {collection_name} already exists")



def get_reference(self, obj, reference_name: str):
    property_name = reference_name[0].lower() + reference_name[1:]
    uuid = obj.properties.get(property_name)

    return self._get_reference(reference_name, uuid)

def _get_reference(self, reference_name: str, reference_id: str):
    reference_collection = self.get_collection(reference_name)
    objects = {obj.uuid: obj for obj in reference_collection.iterator()}
    for uuid, obj in objects.items():
        if uuid == reference_id:
            return obj


def query_reference_context(
    self, collection_name: str, query: str, reference_name: str, top_k: int = 5, k: int = 1, lambda_param=0.5
):
    collection = self.get_collection(collection_name)
    results = collection.query.near_text(query, limit=top_k, include_vector=True, return_metadata=["distance"])
    
    selected = maximal_marginal_relevance(results.objects, k, lambda_param)
    selected_references = [self.get_reference(obj, reference_name).properties for obj in selected]
    return selected_references



if __name__ == "__main__":

    weaviate_client = Weaviate(
        embedding_model=CONFIG.embedding_model, wcs_cluster_url=WCS_CLUSTER_URL
    )
    # Define constants
    COLLECTION_NAME_CERN = "LHC_Brochure_2021"
    COLLECTION_NAME_REFERENCE_CERN = "Originals_LHC_Brochure_2021"
    PROPERTY_NAME_TEXT = "text"
    PROPERTY_DATA_TYPE_TEXT = wvc.config.DataType.TEXT
    REFERENCE_NAME_ORIGINAL_DOC = "original_doc"
    REFERENCE_TEXT = "some reference text"
    DOCUMENT_TEXT = "some text"

    with weaviate_client as client:
        """ for col in client.client.collections.list_all():
            if "LHC" in col:
                client.client.collections.delete(col) """

        # print(client.client.collections.list_all().keys())

        # collection_name = "Quick_Facts_CERN_2021"
        # reference_name = f"Originals_{collection_name}"
        # cern_collection = client.get_collection(collection_name)
        # reference_collection = client.get_collection(reference_name)
        # for obj in cern_collection.iterator():
        #     print(obj.properties['content'])
        #     uuid = (obj.properties.get(COLLECTION_NAME_REFERENCE_CERN))
        #     print(uuid)
        # print(client.get_reference(obj, COLLECTION_NAME_REFERENCE_CERN))

        query = "What is the LHC?"
        result = client.query_reference_context(COLLECTION_NAME_CERN, query, COLLECTION_NAME_REFERENCE_CERN, top_k=10, k=3)
        separator = "\n"*2 + "=" * 50 + "\n"*2
        context = f"{separator}".join([res['content'] for res in result])
        print(context)
       
        # print(len(result))
        for col in client.client.collections.list_all():
            if "LHC" in col:
                print(f"{col}: {len(list(client.get_collection(col).iterator()))}")


        """ for obj in client.get_collection(COLLECTION_NAME_CERN).iterator():
            print(obj.properties['type'], obj.properties['originals_LHC_Brochure_2021']) """
            # print(obj.uuid)
            
        # client.client.collections.delete_all()
