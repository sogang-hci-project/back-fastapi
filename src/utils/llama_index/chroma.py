import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="src/representations")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-mpnet-base-v2"
)
collection = client.get_or_create_collection(
    name="picasso_kg_collection_wikipedia_core",
    embedding_function=sentence_transformer_ef,
)


def check_chroma_db():
    print(f"ChromaDB heartbeat at {client.heartbeat()} 💓")
    print(f"Loaded [{collection.name}] with {collection.count()} number of nodes")


def retreive_node_by_id(id: str):
    try:
        retrieved_node = collection.get(ids=[id])
        retrieved_node_text = retrieved_node["documents"][0]

        if not isinstance(retrieved_node_text, str):
            raise ValueError("Retrieved node is not a string")

        return retrieved_node_text
    except Exception as e:
        print(
            "🔥 utils/llama_index/chroma: [retrieve_node_by_id] Getting node by id failed",
            e,
        )
