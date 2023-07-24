import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="src/representations")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-mpnet-base-v2"
)
collection = client.get_or_create_collection(
    name="picasso_collection", embedding_function=sentence_transformer_ef
)


def check_chroma_db():
    print(f"ChromaDB heartbeat at {client.heartbeat()} 💓")
    print(f"Loaded [{collection.name}] with {collection.count()} number of nodes")
