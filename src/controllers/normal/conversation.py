from fastapi import APIRouter, Request, HTTPException
import uuid
from typing import Dict
from fastapi.responses import PlainTextResponse, StreamingResponse
import io
from pydantic import BaseModel
from src.utils.api import papago_translate, deepl_translate, clova_text_to_speech
from src.utils.common import server_translate
from src.utils.redis import getArrayDialogue, appendDialogue
from src.utils.openai.common import getPicassoAnswerFewShot


async def conversation_request_response(
    stage: int, user: str, lang: str, sessionID: str
):
    agent = ""
    currentStage = ""
    nextStage = ""

    if lang == "ko":
        user = await server_translate(user, source_lang=lang)

    await appendDialogue(sessionID=sessionID, content=user, role="user")

    try:
        dialogue = await getArrayDialogue(sessionID=sessionID)
        agent = await getPicassoAnswerFewShot(dialogue=dialogue, attempt_count=0)
        currentStage = "/conversation/0"
        nextStage = "/conversation/0"
    except Exception as e:
        print("🔥 controller/conversation: [conversation] failed 🔥", e)

    await appendDialogue(sessionID=sessionID, content=agent, role="assistant")

    print("Final Agent Answer: ", agent)

    if lang == "ko":
        agent = await server_translate(agent, source_lang="en")

    return {
        "data": {
            "contents": {
                "agent": agent,
            },
            "currentStage": currentStage,
            "nextStage": nextStage,
        }
    }
