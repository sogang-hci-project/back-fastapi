from fastapi import APIRouter, Request, HTTPException
import uuid
from typing import Dict
from fastapi.responses import PlainTextResponse, StreamingResponse
import io
from pydantic import BaseModel
from src.utils.api import papago_translate, deepl_translate, clova_text_to_speech
from src.utils.common import server_translate
from src.utils.redis import getStringDialogue, appendDialogue, getLastPicassoMessage


async def greeting_request_response(stage: int, user: str, lang: str, sessionID: str):
    agent = ""
    currentStage = ""
    nextStage = ""

    if lang == "ko":
        user = await server_translate(user, source_lang=lang)

    await appendDialogue(sessionID=sessionID, message=user, actor="Friend")

    if stage == 1:
        try:
            agent = "Welcome my friend, Can you tell me about yourname?"
            currentStage = "/greeting/1"
            nextStage = "/greeting/2"
        except Exception as e:
            print("🔥 controller/greeting: [greeting/1] failed 🔥", e)
    elif stage == 2:
        try:
            agent = "Indeed. Its such wonderful to meet you here. What brings you here?"
            currentStage = "/greeting/2"
            nextStage = "/greeting/3"
        except Exception as e:
            print("🔥 controller/greeting: [greeting/2] failed 🔥", e)
    elif stage == 3:
        try:
            agent = "I'm so glad to introduce you my painting the Guernica. Come, would you like to join in?"
            currentStage = "/greeting/2"
            nextStage = "/greeting/3"
        except Exception as e:
            print("🔥 controller/greeting: [greeting/2] failed 🔥", e)

    await appendDialogue(sessionID=sessionID, message=agent, actor="Picasso")

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
