import networkx as nx
from src.utils.redis import (
    get_string_dialogue_as_teacher,
    get_last_directive_from_redis,
    append_directive,
    append_analysis,
    get_last_analysis_from_redis,
    save_networkx_graph,
    get_networkx_graph,
)
from src.utils.openai.graph import (
    get_student_analysis,
    get_directives,
    extract_core_subject,
)
from src.utils.common import (
    neo4j_entities,
    replace_entity_to_picasso,
    cosine_similarity,
)
from src.utils.neo4j.common import (
    find_multiple_pathes_between_two_entity,
    find_path_to_nearest_event_entity,
)
from src.utils.openai.user_graph import extract_entity_from_user_message
from src.utils.langchain.common import embed_model
from src.utils.networkx import (
    get_closest_user_entities,
    get_closest_information_entities,
)


async def generate_pedagogic_strategy(sessionID: str, user: str, agent: str):
    try:
        dialogue = await get_string_dialogue_as_teacher(sessionID=sessionID)
        previous_analysis = await get_last_analysis_from_redis(sessionID=sessionID)
        analysis = await get_student_analysis(
            dialogue=dialogue,
            previous_analysis=previous_analysis,
            user_message=user,
            assistant_message=agent,
            attempt_count=0,
        )
        res = await append_analysis(sessionID=sessionID, content=analysis)
        previous_directives = await get_last_directive_from_redis(sessionID=sessionID)
        directives = await get_directives(
            analysis=analysis,
            previous_directives=previous_directives,
            user_message=user,
            assistant_message=agent,
            attempt_count=0,
        )
        directives = replace_entity_to_picasso(directives)
        res = await append_directive(sessionID=sessionID, content=directives)
    except Exception as e:
        print("🔥 services/graph: [generate_pedagogic_strategy] failed 🔥", e)


async def get_closest_entities(subject: str):
    try:
        subject_emb = embed_model.get_text_embedding(subject)
        entity = ""
        value_flag = 0

        for i, entity_item in enumerate(neo4j_entities):
            new_value = cosine_similarity(subject_emb, entity_item[1])
            if new_value > value_flag:
                value_flag = new_value
                entity = entity_item[0]

        # print("■■■■■■■■■[Closest-Entity-to-Keyword]■■■■■■■■■")
        # print(f"Closest entity for '{subject}': {entity}")

        return entity
    except Exception as e:
        print("🔥 services/graph: [get_closest_entities] failed 🔥", e)


async def update_user_graph(user: str, last_picasso_message: str, sessionID: str):
    try:
        entities = await extract_entity_from_user_message(
            user_message=user, assistant_message=last_picasso_message, attempt_count=0
        )
        user_graph = await get_networkx_graph(sessionID=sessionID)
        entity_for_print_list = ""
        for entity_item in entities:
            entity_item_embedding = embed_model.get_text_embedding(entity_item.content)
            user_graph.add_node(
                entity_item.content,
                content=entity_item.content,
                label=entity_item.type,
                embedding=entity_item_embedding,
            )
            entity_for_print_list += (
                f"LABEL:{entity_item.type}, CONTENT:{entity_item.content}\n"
            )
        for entity_item in entities:
            if len(entity_item.relation) == 2:
                node_one, node_two = entity_item.relation
                node_one_embed = user_graph.nodes[node_one]["embedding"]
                node_two_embed = user_graph.nodes[node_two]["embedding"]
                if node_one_embed and node_two_embed:
                    distance = cosine_similarity(node_one_embed, node_two_embed)
                    user_graph.add_edge(node_one, node_two, distance=distance)
        await save_networkx_graph(sessionID=sessionID, user_graph=user_graph)

        print("■■■■■■■■■[User-Graph-Update]■■■■■■■■■")
        print(entity_for_print_list)
    except Exception as e:
        print("🔥 services/graph: [update_user_graph] failed 🔥", e)


async def get_core_subjects(sessionID: str, user: str, last_picasso_message: str):
    try:
        picasso_core_subjects = []

        if last_picasso_message != "":
            new_picasso_subject = await extract_core_subject(
                sentence=last_picasso_message, attempt_count=0
            )
            picasso_core_subjects.extend(new_picasso_subject)
        user_core_subjects = await extract_core_subject(sentence=user, attempt_count=0)
        core_subjects = picasso_core_subjects + user_core_subjects

        print("■■■■■■■■■[Extracted-Core-Subjects]■■■■■■■■■")
        print(core_subjects)

        return core_subjects
    except Exception as e:
        print("🔥 services/graph: [get_core_subjects] failed 🔥", e)
        return []


def remove_duplicates_entity_by_content(input_array):
    property_values_seen = set()
    result = []

    for item in input_array:
        current_property_value = item.content

        if current_property_value not in property_values_seen:
            result.append(item)
            property_values_seen.add(current_property_value)

    return result


async def get_supplementary_entities(core_subjects: list, user_graph: nx.Graph):
    try:
        supplementary_entities = []
        conversation_entities = []
        for core_subject in core_subjects:
            core_user_entity = await get_closest_user_entities(
                core_subject["keyword"], user_graph
            )
            core_entity = await get_closest_entities(core_subject["keyword"])
            picasso_related_entities = find_multiple_pathes_between_two_entity(
                entity_1_name="Pablo_Picasso",
                entity_2_name=core_entity,
                count=10,
            )
            nearest_event_entities = await find_path_to_nearest_event_entity(
                entity_name=core_entity, count=3
            )
            nearest_user_event_entities = await get_closest_information_entities(
                entity_name=core_user_entity, user_graph=user_graph
            )
            supplementary_entities.extend(nearest_event_entities)
            supplementary_entities.extend(picasso_related_entities)
            conversation_entities.extend(nearest_user_event_entities)

        supplementary_entities_unique = remove_duplicates_entity_by_content(
            supplementary_entities
        )
        conversation_entities_unique = remove_duplicates_entity_by_content(
            conversation_entities
        )

        print("■■■■■■■■■[Supplementary-Entities]■■■■■■■■■")
        for entity_item in supplementary_entities_unique:
            print(f"{entity_item.node_type}: {entity_item.content}")
        print("■■■■■■■■■[Conversation-Entities]■■■■■■■■■")
        for entity_item in conversation_entities_unique:
            print(f"{entity_item.node_type}: {entity_item.content}")

        return supplementary_entities_unique, conversation_entities_unique
    except Exception as e:
        print("🔥 services/graph: [get_supplementary_entities] failed 🔥", e)
        return []
