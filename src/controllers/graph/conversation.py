from fastapi import APIRouter, Request, HTTPException
import uuid
from typing import Dict
from fastapi.responses import PlainTextResponse, StreamingResponse
import io
from pydantic import BaseModel
from src.utils.api import papago_translate, deepl_translate, clova_text_to_speech
from src.utils.common import server_translate
from src.utils.redis import (
    getArrayDialogue,
    appendDialogue,
    appendKoreanDialogue,
    isTimeSpanOver,
    get_last_directive_from_redis,
    getLastPicassoMessage,
    save_networkx_graph,
    get_networkx_graph,
)
from src.utils.openai.graph import (
    get_picasso_answer_few_shot_graph,
    get_picasso_answer_few_shot_graph_using_entity,
    retrieve_subjects,
    extract_core_subject,
)
from src.utils.common import run_task_in_background, replace_entity_to_picasso
from src.services.graph import (
    generate_pedagogic_strategy,
    get_closest_entities,
    update_user_graph,
    get_closest_user_entities,
    get_core_subjects,
    get_supplementary_entities,
    get_user_entities,
    get_next_question_topic,
)
from src.utils.neo4j.common import (
    find_shortest_path_between_two_entity,
    find_path_to_nearest_event_entity,
    find_multiple_pathes_between_two_entity,
)
from src.utils.networkx import get_most_dense_entity


async def conversation_request_graph_response(
    stage: int, user: str, lang: str, sessionID: str
):
    agent = ""
    currentStage = ""
    nextStage = ""

    ## [PRE-TRANSLATE]

    try:
        if lang == "ko":
            await appendKoreanDialogue(sessionID=sessionID, content=user, role="user")
            user = await server_translate(user, source_lang=lang)

        await appendDialogue(sessionID=sessionID, content=user, role="user")
    except Exception as e:
        print("🔥 controller/conversation: [conversation/0][pre-translate] failed 🔥", e)

    ## [GRAPH LOADING]

    try:
        user_graph = await get_networkx_graph(sessionID=sessionID)
        print("■■■■■■■■■[User-Graph-Status]■■■■■■■■■")
        print(
            f"Number of user nodes: {len(user_graph.nodes())} Number of user graph: {len(user_graph.edges())}"
        )
        most_dense_user_entity = await get_most_dense_entity(
            user_graph=user_graph, sessionID=sessionID
        )
        # print(user_graph.nodes())
    except Exception as e:
        print("🔥 controller/conversation: [conversation/0][graph-load] failed 🔥", e)

    ## [ENTITY EXTRACTION]

    try:
        question_topic = await get_next_question_topic(
            user_entity=most_dense_user_entity, sessionID=sessionID
        )
        last_picasso_message = await getLastPicassoMessage(sessionID=sessionID)
        core_subjects = await get_core_subjects(
            sessionID=sessionID, user=user, last_picasso_message=last_picasso_message
        )
        supplementary_entities = await get_supplementary_entities(
            core_subjects=core_subjects
        )
        user_entities = await get_user_entities(
            core_subjects=core_subjects, user_graph=user_graph
        )
    except Exception as e:
        print(
            "🔥 controller/conversation: [conversation/0][entity-extraction] failed 🔥",
            e,
        )

    ## [RESPONSE GENERATION]

    try:
        dialogue = await getArrayDialogue(sessionID=sessionID)
        directive = await get_last_directive_from_redis(sessionID=sessionID)

        agent = await get_picasso_answer_few_shot_graph_using_entity(
            dialogue=dialogue[:-1],
            attempt_count=0,
            user_message=user,
            directive=directive,
            entities=supplementary_entities,
            user_entities=user_entities,
            next_topic=question_topic,
        )
    except Exception as e:
        print(
            "🔥 controller/conversation: [conversation/0][response-generation] failed 🔥",
            e,
        )

    ## [STAGE-CALCULATION]

    try:
        currentStage = "/conversation/0"
        is_over = await isTimeSpanOver(sessionID=sessionID)
        if is_over:
            nextStage = "/farewell/0"
        else:
            nextStage = "/conversation/0"
    except Exception as e:
        print(
            "🔥 controller/conversation: [conversation/0][stage-calculation] failed 🔥",
            e,
        )

    ## [SELF-EVALUATION]

    try:
        run_task_in_background(
            update_user_graph(
                user=user,
                last_picasso_message=last_picasso_message,
                sessionID=sessionID,
            )
        )
        # run_task_in_background(
        #     generate_pedagogic_strategy(sessionID=sessionID, user=user, agent=agent)
        # )
        await appendDialogue(sessionID=sessionID, content=agent, role="assistant")

    except Exception as e:
        print(
            "🔥 controller/conversation: [conversation/0][self-evaluation] failed 🔥", e
        )

    ## [POST TRNASLATE]

    try:
        if lang == "ko":
            agent = await server_translate(agent, source_lang="en")
            await appendKoreanDialogue(
                sessionID=sessionID, content=agent, role="assistant"
            )

    except Exception as e:
        print("🔥 controller/conversation: [conversation/0][post-translate] failed 🔥", e)

    print("Final Agent Answer: ", agent)

    return {
        "data": {
            "contents": {
                "agent": agent,
            },
            "currentStage": currentStage,
            "nextStage": nextStage,
        }
    }
