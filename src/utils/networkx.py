import networkx as nx
from src.utils.langchain.common import embed_model
from src.utils.common import (
    cosine_similarity,
)


async def get_closest_user_entities(subject: str, user_graph: nx.Graph):
    try:
        subject_emb = embed_model.get_text_embedding(subject)
        entity = ""
        value_flag = 0
        user_nodes = user_graph.nodes()

        for node_item in user_nodes:
            if user_graph.nodes[node_item]["label"] == "ENTITY":
                new_value = cosine_similarity(
                    subject_emb, user_graph.nodes[node_item]["embedding"]
                )
                if new_value > value_flag:
                    value_flag = new_value
                    entity = node_item

        if len(user_nodes) > 0:
            print("■■■■■■■■■[Closest-User-Entity-to-Keyword]■■■■■■■■■")
            print(f"Closest entity for '{subject}': {entity}")
            return entity
        else:
            return ""

    except Exception as e:
        print("🔥 services/graph: [get_closest_user_entities] failed 🔥", e)
        return ""
