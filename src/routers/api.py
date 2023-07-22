from fastapi import APIRouter, Request, HTTPException
import uuid
from typing import Dict
from fastapi.responses import PlainTextResponse, StreamingResponse
import io
from pydantic import BaseModel
from src.utils.api import papago_translate, deepl_translate, clova_text_to_speech
from src.controllers.greeting import greeting_request_response


class ClientRequest(BaseModel):
    user: str


router = APIRouter()

"""
UTILITY ROUTING
"""


@router.post("/api/v1/greeting/0", tags=["api"])
async def handle_request_zero():
    try:
        id = str(uuid.uuid4())
        return {
            "data": {
                "sessionID": id,
                "currentStage": "/greeting/0",
                "nextStage": "/greeting/1",
            }
        }
    except Exception as e:
        print("🔥 router/api: [greeting/0] failed 🔥", e)
        raise HTTPException(status_code=500, detail="router/api: [greeting/0] failed")


@router.post("/api/v1/greeting/{stage}")
async def handle_greeting_request(
    stage: int,
    req: ClientRequest,
    sessionID: str,
    lang: str,
):
    try:
        response = await greeting_request_response(
            stage, user=req.user, sessionID=sessionID, lang=lang
        )
        return response
    except Exception as e:
        print("🔥 router/api: [greeting/1] failed 🔥", e)
        raise HTTPException(status_code=500, detail="router/api: [greeting/1] failed")


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
        raise HTTPException(status_code=500, detail="Internal server error.")
