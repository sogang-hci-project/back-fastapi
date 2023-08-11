from fastapi import APIRouter, Request, HTTPException
import uuid
from typing import Dict
from fastapi.responses import PlainTextResponse, StreamingResponse
import io
from pydantic import BaseModel
from src.utils.common import server_translate
from src.utils.redis import (
    getArrayDialogue,
    appendDialogue,
    getStringDialogue,
    appendKoreanDialogue,
    isTimeSpanOver,
    get_networkx_graph,
)
from src.utils.openai.common import getPicassoAnswerFewShot, get_GPT_translation
from src.services.graph import update_user_graph

message_by_stage = [
    {
        "en": "Welcome. My name is Pablo Picasso, a spanish painter. Can you introduce yourself?",
        "ko": "환영합니다, 저는 파블로 피카소라고 하는 스페인의 화가입니다. 당신에 대해 소개해줄 수 있나요?",
    },
    {
        "en": "Indeed. Its such wonderful to meet you here. What brings you here?",
        "ko": "그렇군요, 여기서 만나게 되서 정말 기뻐요. 어떻게 이곳에 오게 되었나요?",
    },
    {
        "en": "I'm so glad to introduce you my painting the Guernica. Come, would you like to join in?",
        "ko": "당신에게 저의 그림 게르니카를 소개할 수 있어서 정말 기쁩니다. 함께 저와 그림을 감상하시겠어요?",
    },
    {
        "en": "What's going on in this picture?",
        "ko": "그림에서 무슨 일이 일어나고 있나요?",
    },
    {
        "en": "What do you see that makes you say that?",
        "ko": "무엇을 보고 그렇게 말하셨나요?",
    },
]


async def greeting_request_graph_response(
    stage: int, user: str, lang: str, sessionID: str
):
    agent = ""
    currentStage = ""
    nextStage = ""

    ## [PRE-TRANSLATE]

    try:
        if lang == "ko" and user != "hello":
            await appendKoreanDialogue(sessionID=sessionID, content=user, role="user")
            user = await get_GPT_translation(user, source_lang=lang, attempt_count=0)
        await appendDialogue(sessionID=sessionID, content=user, role="user")
    except Exception as e:
        print("🔥 controller/greeting: [pre-translate] failed 🔥", e)

    ## [ENTITY EXTRACTION]

    try:
        user_graph = await get_networkx_graph(sessionID=sessionID)
        print("■■■■■■■■■[User-Graph-Status]■■■■■■■■■")
        print(
            f"Number of user nodes: {len(user_graph.nodes())} Number of user graph: {len(user_graph.edges())}"
        )
    except:
        print(
            "🔥 controller/greeting: [entity-extraction] failed 🔥",
            e,
        )

    ## [RESPONSE-GENERATION]

    try:
        if stage == 0:
            agent = message_by_stage[stage][lang]
            currentStage = "/greeting/0"
            nextStage = "/greeting/1"
        elif stage == 1:
            agent = message_by_stage[stage][lang]
            currentStage = "/greeting/1"
            nextStage = "/greeting/2"
        elif stage == 2:
            agent = message_by_stage[stage][lang]
            currentStage = "/greeting/2"
            nextStage = "/greeting/3"
        elif stage == 3:
            agent = message_by_stage[stage][lang]
            currentStage = "/greeting/3"
            nextStage = "/greeting/4"
        elif stage == 4:
            agent = message_by_stage[stage][lang]
            currentStage = "/greeting/4"
            nextStage = "/conversation/0"
    except Exception as e:
        print("🔥 controller/greeting: [response-generation] failed 🔥", e)

    ## [SELF-EVALUATION]

    try:
        await update_user_graph(
            user=user,
            last_picasso_message=agent,
            sessionID=sessionID,
        )
        await appendDialogue(sessionID=sessionID, content=agent, role="assistant")

    except Exception as e:
        print(
            "🔥 controller/conversation: [conversation/0][self-evaluation] failed 🔥", e
        )

    ## [POST TRANSLATE]

    try:
        await appendDialogue(
            sessionID=sessionID, content=message_by_stage[stage]["en"], role="assistant"
        )
        if lang == "ko":
            await appendKoreanDialogue(
                sessionID=sessionID,
                content=message_by_stage[stage]["ko"],
                role="assistant",
            )
    except Exception as e:
        print("🔥 controller/greeting: [post-translate] failed 🔥", e)

    return {
        "data": {
            "contents": {
                "agent": agent,
            },
            "currentStage": currentStage,
            "nextStage": nextStage,
        }
    }
