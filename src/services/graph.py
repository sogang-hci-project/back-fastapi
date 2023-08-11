from src.utils.redis import (
    get_string_dialogue_as_teacher,
    get_last_directive_from_redis,
    append_directive,
    append_analysis,
    get_last_analysis_from_redis,
)
from src.utils.openai.graph import (
    get_student_analysis,
    get_directives,
)
from src.utils.common import (
    neo4j_entities,
    replace_entity_to_picasso,
    cosine_similarity,
)
from src.utils.langchain.common import embed_model


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

        print("■■■■■■■■■[Closest-Entity-to-Keyword]■■■■■■■■■")
        print(f"Closest entity for '{subject}': {entity}")

        return entity
    except Exception as e:
        print("🔥 services/graph: [get_closest_entities] failed 🔥", e)
