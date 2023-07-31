from fastapi import APIRouter, Request, HTTPException, UploadFile
import uuid
from typing import Dict
from fastapi.responses import PlainTextResponse, StreamingResponse
import io
from pydantic import BaseModel
from datetime import datetime
import json

from src.utils.openai.common import whisper_speech_to_text
from src.utils.api import papago_translate, deepl_translate, clova_text_to_speech
from src.controllers.normal.greeting import greeting_request_response
from src.controllers.normal.conversation import conversation_request_response
from src.controllers.normal.farewell import farewell_request_response
from src.utils.redis import redisEndPoint


class ClientRequest(BaseModel):
    user: str


router = APIRouter()

"""
UTILITY ROUTING
"""


@router.post("/api/v1/register", tags=["api"])
async def handle_request_zero():
    try:
        id = str(uuid.uuid4())
        current = datetime.now().strftime("%m-%d %H:%M:%S")
        id_current = id + "-" + datetime.now().strftime("%m-%d-%H-%M")
        current_timestamp = datetime.now().timestamp()
        data = {
            "init": current,
            "init-timestamp": current_timestamp,
        }
        await redisEndPoint.set(f"sess:{id_current}", value=json.dumps(data))

        return {
            "data": {
                "sessionID": id_current,
                "currentStage": "/register",
                "nextStage": "/greeting/0",
            }
        }
    except Exception as e:
        print("🔥 router/api: [register] failed 🔥", e)
        raise HTTPException(status_code=500, detail="router/api: [register] failed")


@router.post("/api/v1/{mode}/greeting/{stage}")
async def handle_greeting_request(
    stage: int,
    req: ClientRequest,
    sessionID: str,
    lang: str,
    mode: str,
):
    try:
        if mode == "normal":
            response = await greeting_request_response(
                stage, user=req.user, sessionID=sessionID, lang=lang
            )
            return response
        elif mode == "graph":
            return {"": ""}
    except Exception as e:
        print("🔥 router/api: [greeting] failed 🔥", e)
        raise HTTPException(status_code=500, detail="router/api: [greeting] failed")


@router.post("/api/v1/{mode}/conversation/{stage}")
async def handle_conversation_request(
    stage: int,
    req: ClientRequest,
    sessionID: str,
    lang: str,
    mode: str,
):
    try:
        if mode == "normal":
            response = await conversation_request_response(
                stage, user=req.user, sessionID=sessionID, lang=lang
            )
            return response
        elif mode == "graph":
            return {"": ""}
    except Exception as e:
        print("🔥 router/api: [conversation] failed 🔥", e)
        raise HTTPException(status_code=500, detail="router/api: [conversation] failed")


@router.post("/api/v1/{mode}/farewell/{stage}")
async def handle_farewell_request(
    stage: int,
    req: ClientRequest,
    sessionID: str,
    lang: str,
    mode: str,
):
    try:
        if mode == "normal":
            response = await farewell_request_response(
                stage, user=req.user, sessionID=sessionID, lang=lang
            )
            return response
        elif mode == "graph":
            return {"": ""}
    except Exception as e:
        print("🔥 router/api: [farewell] failed 🔥", e)
        raise HTTPException(status_code=500, detail="router/api: [farewell] failed")


"""
UTILITY ROUTING
"""


@router.post("/api/v1/util/translate", tags=["api"])
async def handle_translate(request: Request) -> Dict[str, str]:
    try:
        source_lang = request.query_params.get("lang")
        data = await request.json()
        text = data.get("text", "")

        if not source_lang or not text:
            raise HTTPException(status_code=400, detail="Invalid request parameters.")

        translated_text = await deepl_translate(text, source_lang)

        return {"message": "Translation complete.", "translatedText": translated_text}
    except Exception as e:
        print("🔥 router/api: [util/translate] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="router/api: [util/translate] failed"
        )


@router.post("/api/v1/util/texttospeech", tags=["api"])
async def handle_text_to_speech(request: Request, response_class=PlainTextResponse):
    try:
        data = await request.json()
        text = data.get("text", " ")
        voice = data.get("voice", "")

        if not text or not voice:
            raise HTTPException(status_code=400, detail="Invalid request parameters.")

        decoded_audio = await clova_text_to_speech(text, voice)

        return StreamingResponse(io.BytesIO(decoded_audio), media_type="audio/mpeg")
    except Exception as e:
        print("🔥 router/api: [util/texttospeech] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="router/api: [util/texttospeech] failed"
        )


@router.post("/api/v1/util/speechtotext", tags=["api"])
async def handle_speech_to_text(file: UploadFile):
    try:
        result = await whisper_speech_to_text(file=file.file, count=0)
        print("[SERVICE UTIL] Whisper Paraphrase: ", result)
        return {"text", result}
    except Exception as e:
        print("🔥 router/api: [util/speechtotext] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="router/api: [util/speechtotext] failed"
        )
