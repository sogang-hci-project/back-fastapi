from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.vector_stores import ChromaVectorStore
from llama_index.storage.storage_context import StorageContext
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index.embeddings import LangchainEmbedding
from src.utils.llama_index.chroma import collection
from llama_index.indices.vector_store.retrievers import VectorIndexRetriever


embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
)

vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
service_context = ServiceContext.from_defaults(embed_model=embed_model)

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context,
    service_context=service_context,
)

retriever = VectorIndexRetriever(index=index, similarity_top_k=5)


async def retrieve_relevent_nodes_in_string(text: str):
    node_reps = retriever.retrieve(text)
    res = "\n\n".join(
        list(map(lambda node_rep: node_rep.node.get_content(), node_reps))
    )
    return res
