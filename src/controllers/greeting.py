from fastapi import APIRouter, Request, HTTPException
import uuid
from typing import Dict
from fastapi.responses import PlainTextResponse, StreamingResponse
import io
from pydantic import BaseModel
from src.utils.api import papago_translate, deepl_translate, clova_text_to_speech


async def greeting_request_response(stage: int, user: str, lang: str, sessionID: str):
    agent = ""
    currentStage = ""
    nextStage = ""

    if stage == 1:
        try:
            agent = "안녕하세요"
            currentStage = "greeting/1"
            nextStage = "gretting/2"
        except Exception as e:
            print("🔥 controller/greeting: [greeting/1] failed 🔥", e)

    return {
        "data": {
            "contents": {
                "agent": agent,
                "currentStage": currentStage,
                "nextStage": nextStage,
            }
        }
    }
