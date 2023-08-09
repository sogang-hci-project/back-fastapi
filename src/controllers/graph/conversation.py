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
)
from src.utils.openai.graph import (
    get_picasso_answer_few_shot_graph,
    retrieve_subjects,
)
from src.utils.common import run_task_in_background, replace_entity_to_picasso
from src.services.graph import generate_pedagogic_strategy, get_closest_entities


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

    ## [RESPONSE GENERATION]

    try:
        dialogue = await getArrayDialogue(sessionID=sessionID)
        isOver = await isTimeSpanOver(sessionID=sessionID)
        directive = await get_last_directive_from_redis(sessionID=sessionID)
        subjects = await retrieve_subjects(sentence=user, attempt_count=0)
        closest_entities_1 = await get_closest_entities(subjects[0])
        closest_entities_2 = await get_closest_entities(subjects[1])
        print(closest_entities_1, closest_entities_2)

        agent = await get_picasso_answer_few_shot_graph(
            dialogue=dialogue[:-1],
            attempt_count=0,
            user_message=user,
            directive=directive,
        )
        currentStage = "/conversation/0"

        if isOver:
            nextStage = "/farewell/0"
        else:
            nextStage = "/conversation/0"
    except Exception as e:
        print(
            "🔥 controller/conversation: [conversation/0][response-generation] failed 🔥",
            e,
        )

    ## [SELF-EVALUATION]

    try:
        run_task_in_background(
            generate_pedagogic_strategy(sessionID=sessionID, user=user, agent=agent)
        )
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
