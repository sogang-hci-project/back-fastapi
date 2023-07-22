import aioredis
import json
from src.utils.common import throw_exception
from fastapi import HTTPException

redisEndPoint = aioredis.from_url("redis://localhost")


class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


async def initialize():
    res = await redisEndPoint.ping()
    if res == False:
        throw_exception("Redis initialization failed", 500)


"""
Dialogue Structure

[
    {"actor": actor, "message": message}
    {"actor": actor, "message": message}
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
            list(map(lambda x: x["actor"] + ": " + x["message"], dialogue))
        )

        return stringDialogue or ""
    except Exception as e:
        print("🔥 utils/redis: [getStringDialogue] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="router/api: [getStringDialogue] failed"
        )


async def appendDialogue(
    sessionID: str,
    actor: str,
    message: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)

        dialogue = data["dialogue"] if "dialogue" in data else []
        dialogue.append({"actor": actor, "message": message})

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
        message = ""

        for item in reversed(dialogue):
            if item["actor"] == "Picasso":
                message = item["message"]
                break

        return message
    except Exception as e:
        print("🔥 utils/redis: [getLastPicassoMessage] failed 🔥", e)
        raise HTTPException(
            status_code=500, detail="router/api: [getLastPicassoMessage] failed"
        )
