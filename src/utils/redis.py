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


def joinMessageAsSentenceForSupervisor(message: dict[str, str]):
    try:
        role = ""
        if message["role"] == "assistant":
            role = "Art Educator"
        elif message["role"] == "user":
            role = "Student"
        return role + ": " + message["content"]

    except Exception as e:
        print("🔥 utils/redis: [joinMessageAsSentenceForSupervisor] failed 🔥", e)
        raise HTTPException(
            status_code=500,
            detail="router/api: [joinMessageAsSentenceForSupervisor] failed",
        )


async def get_string_dialogue_as_teacher(
    sessionID: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)

        dialogue = data["dialogue"] if "dialogue" in data else []

        stringDialogue = "\n".join(
            list(map(joinMessageAsSentenceForSupervisor, dialogue))
        )

        return stringDialogue or ""
    except Exception as e:
        print("🔥 utils/redis: [get_string_dialogue_as_teacher] failed 🔥", e)
        raise HTTPException(
            status_code=500,
            detail="router/api: [get_string_dialogue_as_teacher] failed",
        )


def remove_key_from_objects(obj_array, key_to_remove):
    for obj in obj_array:
        if key_to_remove in obj:
            del obj[key_to_remove]


async def getArrayDialogue(
    sessionID: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)

        dialogue = data["dialogue"] if "dialogue" in data else []

        remove_key_from_objects(dialogue, "time")

        return dialogue
    except Exception as e:
        print("🔥 utils/redis: [getArrayDialogue] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="utils/redis: [getArrayDialogue] failed"
        )


async def appendDialogue(
    sessionID: str,
    role: str,
    content: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)

        conversation_time = datetime.now().timestamp()
        dialogue = data["dialogue"] if "dialogue" in data else []
        dialogue.append({"time": conversation_time, "role": role, "content": content})

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
        conversation_time = datetime.now().timestamp()
        dialogue.append({"time": conversation_time, "role": role, "content": content})

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


async def isTimeSpanOver(sessionID: str):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)

        init_timestamp = int(data["init-timestamp"])
        current_timestamp = datetime.now().timestamp()
        span = current_timestamp - init_timestamp
        print(
            f"""
            ■■■■■■■■■[TIME SPAN CALCULATION]■■■■■■■■■
            {span} seconds has been passed
            """
        )

        if span > 600:
            print("CONVERSATION ABORTED DUE TO TIME LIMIT, BYE")
            return True
        else:
            return False

    except Exception as e:
        print("🔥 utils/redis: [isTimeSpanOver] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="utils/redis: [isTimeSpanOver] failed"
        )
