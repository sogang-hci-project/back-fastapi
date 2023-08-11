from typing import Union
import time

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.routers import client, api
from src.utils.common import print_project_initialization, load_neo4j_entities
from src.utils.redis import check_redis
from src.utils.openai.initialize import register_openai_variable
from src.utils.llama_index.chroma import check_chroma_db
from src.utils.llama_index.common import retrieve_relevent_nodes_in_string
from src.services.graph import get_closest_entities
from src.utils.neo4j.common import check_auradb_connection

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.include_router(client.router)
app.include_router(api.router)


@app.on_event("startup")
async def initialize_server():
    try:
        print_project_initialization()
        register_openai_variable()
        await check_redis()
        check_chroma_db()
        load_neo4j_entities()
        check_auradb_connection()
    except Exception as e:
        print("🔥 startup: [initialize_server] failed 🔥", e)


@app.middleware("http")
async def log_request(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.mount("/static", StaticFiles(directory="client/build/static"), name="static")
app.mount("/", StaticFiles(directory="client/build"), name="build")
