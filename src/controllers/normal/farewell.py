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
)
from src.utils.openai.common import (
    getPicassoFarewell,
)


async def farewell_request_response(stage: int, user: str, lang: str, sessionID: str):
    agent = ""
    currentStage = ""
    nextStage = ""

    if lang == "ko":
        await appendKoreanDialogue(sessionID=sessionID, content=user, role="user")
        user = await server_translate(user, source_lang=lang)

    try:
        dialogue = await getArrayDialogue(sessionID=sessionID)
        agent = await getPicassoFarewell(
            dialogue=dialogue, attempt_count=0, user_message=user
        )
        currentStage = "/farewell/0"
        nextStage = "/end"
    except Exception as e:
        print("🔥 controller/conversation: [conversation] failed 🔥", e)

    await appendDialogue(sessionID=sessionID, content=user, role="user")
    await appendDialogue(sessionID=sessionID, content=agent, role="assistant")

    print("Final Agent Answer: ", agent)

    if lang == "ko":
        agent = await server_translate(agent, source_lang="en")
        await appendKoreanDialogue(sessionID=sessionID, content=agent, role="assistant")

    return {
        "data": {
            "contents": {
                "agent": agent,
            },
            "currentStage": currentStage,
            "nextStage": nextStage,
        }
    }
