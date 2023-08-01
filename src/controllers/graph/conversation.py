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
    getStringDialogue,
    getLastPicassoMessage,
    isTimeSpanOver,
    get_string_dialogue_as_teacher,
)
from src.utils.openai.common import (
    getPicassoAnswerFewShot,
    getPicassoAnswerFewShotTextDavinci,
)
from src.utils.openai.graph import get_student_analysis, get_directives
from src.utils.common import run_task_in_background


async def generate_pedagogic_strategy(sessionID: str, user: str, agent: str):
    dialogue = await get_string_dialogue_as_teacher(sessionID=sessionID)
    analysis = await get_student_analysis(
        dialogue=dialogue,
        user_message=user,
        assistant_message=agent,
        attempt_count=0,
    )
    directives = await get_directives(
        analysis=analysis, user_message=user, assistant_message=agent, attempt_count=0
    )


async def conversation_request_graph_response(
    stage: int, user: str, lang: str, sessionID: str
):
    agent = ""
    currentStage = ""
    nextStage = ""

    try:
        if lang == "ko":
            await appendKoreanDialogue(sessionID=sessionID, content=user, role="user")
            user = await server_translate(user, source_lang=lang)

        await appendDialogue(sessionID=sessionID, content=user, role="user")
    except Exception as e:
        print("🔥 controller/conversation: [conversation/0][pre-translate] failed 🔥", e)

    try:
        ### ChatGPT3.5 Case ###
        dialogue = await getArrayDialogue(sessionID=sessionID)
        isOver = await isTimeSpanOver(sessionID=sessionID)

        agent = await getPicassoAnswerFewShot(
            dialogue=dialogue[:-1], attempt_count=0, user_message=user
        )
        # string_dialogue = await getStringDialogue(sessionID=sessionID)
        # previous_agent = await getLastPicassoMessage(sessionID=sessionID)
        # agent = await getPicassoAnswerFewShotTextDavinci(
        #     string_dialogue=string_dialogue,
        #     user_message=user,
        #     agent_message=previous_agent,
        #     attempt_count=0,
        # )
        currentStage = "/conversation/0"

        if isOver:
            nextStage = "/farewell/0"
        else:
            nextStage = "/conversation/0"
    except Exception as e:
        print("🔥 controller/conversation: [conversation] failed 🔥", e)
    try:
        run_task_in_background(
            generate_pedagogic_strategy(sessionID=sessionID, user=user, agent=agent)
        )
        await appendDialogue(sessionID=sessionID, content=agent, role="assistant")

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
