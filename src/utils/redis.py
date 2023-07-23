import aioredis
import json
from src.utils.common import throw_exception
from fastapi import HTTPException

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


async def getStringDialogue(
    sessionID: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)

        dialogue = data["dialogue"] if "dialogue" in data else []

        stringDialogue = "\n".join(
            list(map(lambda x: x["role"] + ": " + x["content"], dialogue))
        )

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
            status_code=500, detail="router/api: [getStringDialogue] failed"
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
            status_code=500, detail="router/api: [appendDialogue] failed"
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
            if item["role"] == "Picasso":
                content = item["content"]
                break

        return content
    except Exception as e:
        print("🔥 utils/redis: [getLastPicassoMessage] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="router/api: [getLastPicassoMessage] failed"
        )
