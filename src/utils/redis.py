import aioredis
import json
import networkx as nx
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
    print("Connected to [redis] with everlasting friendship")
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


async def append_directive(
    sessionID: str,
    content: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)

        conversation_time = datetime.now().timestamp()
        directives = data["directive"] if "directive" in data else []
        directives.append({"time": conversation_time, "content": content})

        data["directive"] = directives
        req = json.dumps(data)
        await redisEndPoint.set(f"sess:{sessionID}", req)

        return True
    except Exception as e:
        print("🔥 utils/redis: [append_directive] failed 🔥", e)


async def get_last_directive_from_redis(
    sessionID: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)
        directives = (
            data["directive"] if "directive" in data else [{"time": "", "content": ""}]
        )

        return directives[-1]["content"]
    except Exception as e:
        print("🔥 utils/redis: [get_last_directive_from_redis] failed 🔥", e)
        raise HTTPException(
            status_code=500,
            detail="utils/redis: [get_last_directive_from_redis] failed",
        )


async def append_analysis(
    sessionID: str,
    content: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)

        conversation_time = datetime.now().timestamp()
        analyses = data["analysis"] if "analysis" in data else []
        analyses.append({"time": conversation_time, "content": content})

        data["analysis"] = analyses
        req = json.dumps(data)
        await redisEndPoint.set(f"sess:{sessionID}", req)

        return True
    except Exception as e:
        print("🔥 utils/redis: [append_directive] failed 🔥", e)


async def get_last_analysis_from_redis(
    sessionID: str,
):
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)
        analyses = (
            data["analysis"] if "analysis" in data else [{"time": "", "content": ""}]
        )

        return analyses[-1]["content"]
    except Exception as e:
        print("🔥 utils/redis: [get_last_directive_from_redis] failed 🔥", e)
        raise HTTPException(
            status_code=500,
            detail="utils/redis: [get_last_directive_from_redis] failed",
        )


async def save_networkx_graph(sessionID: str, user_graph: nx.Graph):
    try:
        graph_json = nx.readwrite.json_graph.node_link_data(user_graph)
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)
        data["graph"] = graph_json
        req = json.dumps(data)
        await redisEndPoint.set(f"sess:{sessionID}", req)
    except Exception as e:
        print("🔥 utils/redis: [save_networkx_graph] failed 🔥", e)


async def get_networkx_graph(sessionID: str) -> nx.Graph:
    try:
        res = await redisEndPoint.get(f"sess:{sessionID}")
        data = json.loads(res)
        user_graph = None
        if "graph" in data:
            user_graph = nx.json_graph.node_link_graph(data["graph"])
        else:
            user_graph = nx.Graph()
        return user_graph
    except Exception as e:
        print("🔥 utils/redis: [get_networkx_graph] failed 🔥", e)
        return nx.Graph()
