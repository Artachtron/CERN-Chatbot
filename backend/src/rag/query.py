from weaviate import WeaviateClient


def find_context(
    client: WeaviateClient,
    question: str,
    collection_name: str,
    top_k: int = 3,
) -> list[str]:
    response = client.collections.get(collection_name).query.near_text(
        question, limit=top_k
    )
    return [obj.properties["text"] for obj in response.objects]


def format_context(context: list[str]) -> str:
    return "\n\n".join(context)
