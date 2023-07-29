import aioredis
import json
from src.utils.common import throw_exception
from fastapi import HTTPException
from datetime import datetime

redisEndPoint = aioredis.from_url("redis://localhost")


class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


async def check_redis():
    res = await redisEndPoint.ping()
    if res == False:
        throw_exception("Redis initialization failed", 500)


"""
Dialogue Structure

[
    {"role": role, "content": content}
    {"role": role, "content": content}
]

"""


def joinMessageAsSentence(message: dict[str, str]):
    try:
        role = ""
        if message["role"] == "assistant":
            role = "Picasso"
        elif message["role"] == "user":
            role = "Student"
        return role + ": " + message["content"]

    except Exception as e:
        print("🔥 utils/redis: [joinMessageAsSentence] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="router/api: [joinMessageAsSentence] failed"
        )


async def getStringDialogue(
    sessionID: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)

        dialogue = data["dialogue"] if "dialogue" in data else []

        stringDialogue = "\n".join(list(map(joinMessageAsSentence, dialogue)))

        return stringDialogue or ""
    except Exception as e:
        print("🔥 utils/redis: [getStringDialogue] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="router/api: [getStringDialogue] failed"
        )


async def getArrayDialogue(
    sessionID: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)

        dialogue = data["dialogue"] if "dialogue" in data else []

        return dialogue
    except Exception as e:
        print("🔥 utils/redis: [getStringDialogue] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="utils/redis: [getStringDialogue] failed"
        )


async def appendDialogue(
    sessionID: str,
    role: str,
    content: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)

        dialogue = data["dialogue"] if "dialogue" in data else []
        dialogue.append({"role": role, "content": content})

        data["dialogue"] = dialogue
        req = json.dumps(data)
        await redisEndPoint.set(f"sess:{sessionID}", req)

    except Exception as e:
        print("🔥 utils/redis: [appendDialogue] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="utils/redis: [appendDialogue] failed"
        )


async def appendKoreanDialogue(
    sessionID: str,
    role: str,
    content: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)

        dialogue = data["dialogue_korean"] if "dialogue_korean" in data else []
        dialogue.append({"role": role, "content": content})

        data["dialogue_korean"] = dialogue
        req = json.dumps(data)
        await redisEndPoint.set(f"sess:{sessionID}", req)

    except Exception as e:
        print("🔥 utils/redis: [appendKoreanDialogue] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="utils/redis: [appendKoreanDialogue] failed"
        )


async def getLastPicassoMessage(
    sessionID: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)
        dialogue = data["dialogue"]
        content = ""

        for item in reversed(dialogue):
            if item["role"] == "assistant":
                content = item["content"]
                break

        return content if content else ""
    except Exception as e:
        print("🔥 utils/redis: [getLastPicassoMessage] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="utils/redis: [getLastPicassoMessage] failed"
        )


async def isTimeSpanOver(sessionId: str):
    try:
        res = await redisEndPoint.get(f"sess:{sessionId}")
        data = json.loads(res)
        init_timestamp = int(data["init-timestamp"])
        current_timestamp = datetime.now().timestamp()
        span = current_timestamp - init_timestamp
        print(span)
        # return span > 600
        return False

    except Exception as e:
        print("🔥 utils/redis: [isTimeSpanOver] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="utils/redis: [isTimeSpanOver] failed"
        )
