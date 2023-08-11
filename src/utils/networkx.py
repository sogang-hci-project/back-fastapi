import networkx as nx
from src.utils.langchain.common import embed_model
from src.utils.common import (
    cosine_similarity,
)
from src.utils.redis import get_user_topic_list
from src.utils.neo4j.common import Neo4jNode
from typing import List


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
            # print("■■■■■■■■■[Closest-User-Entity-to-Keyword]■■■■■■■■■")
            # print(f"Closest entity for '{subject}': {entity}")
            return entity
        else:
            return ""

    except Exception as e:
        print("🔥 utils/networkx: [get_closest_user_entities] failed 🔥", e)
        return ""


async def get_closest_information_entities(
    entity_name: str, user_graph: nx.Graph
) -> List[Neo4jNode]:
    try:
        if len(user_graph.nodes()) == 0 or len(user_graph.edges()) == 0:
            return []

        information_entities = []

        target_neighbors = list(user_graph.neighbors(entity_name))
        for entity_item in target_neighbors:
            if user_graph.nodes[entity_item]["label"] != "ENTITY":
                entity_item_props = user_graph.nodes[entity_item]
                node_entity_item = Neo4jNode(
                    node_label=["NETWORKX", entity_item_props["label"]],
                    node_type=entity_item_props["label"],
                    name=entity_item,
                    content=entity_item,
                    node_id=None,
                )

                information_entities.append(node_entity_item)

        return information_entities
    except Exception as e:
        print("🔥 utils/networkx: [get_closest_information_entities] failed 🔥", e)
        return []


async def get_most_dense_entity(user_graph: nx.Graph, sessionID: str):
    try:
        if len(user_graph.nodes()) == 0:
            return ""
        user_nodes = user_graph.nodes()
        user_entities = []
        topic_list = await get_user_topic_list(sessionID=sessionID)

        filter_list = ["picasso", "student", "guernica"]
        filter_list.extend(topic_list)

        for node_item in user_nodes:
            if user_graph.nodes[node_item]["label"] == "ENTITY":
                user_entities.append(node_item)

        relation_counts = {
            entity: len(list(user_graph.neighbors(entity))) for entity in user_entities
        }
        sorted_entities = sorted(
            relation_counts.keys(), key=lambda x: relation_counts[x], reverse=True
        )
        final_entities = list(
            filter(lambda item: item not in filter_list, sorted_entities)
        )
        return final_entities[0]
    except Exception as e:
        print("🔥 utils/networkx: [get_most_dense_entity] failed 🔥", e)
        return ""
