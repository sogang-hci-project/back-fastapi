from fastapi import APIRouter, Request, HTTPException
import uuid
from typing import Dict
from fastapi.responses import PlainTextResponse, StreamingResponse
import io
from pydantic import BaseModel
from src.utils.api import papago_translate, deepl_translate, clova_text_to_speech
from src.utils.common import server_translate


async def greeting_request_response(stage: int, user: str, lang: str, sessionID: str):
    agent = ""
    currentStage = ""
    nextStage = ""

    if lang == "ko":
        user = await server_translate(user, source_lang=lang)

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
