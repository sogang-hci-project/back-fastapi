from typing import Union

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.routers import client, api

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.include_router(client.router)
app.include_router(api.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.mount("/static", StaticFiles(directory="client/build/static"), name="static")
app.mount("/", StaticFiles(directory="client/build"), name="build")
