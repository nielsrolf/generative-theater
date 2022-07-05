from fastapi import FastAPI
import uvicorn
import click
from pydantic import BaseModel
from typing import List
import shutil
import os
import json

app = FastAPI()

assets_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "frontend", "public", "current_story")


class StoryRequest(BaseModel):
    path: str


class MediaFile(BaseModel):
    src: str
    output: str
    text: str


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/files/")
async def get_files(story_request: StoryRequest) -> List[MediaFile]:
    shutil.copytree(story_request.path, assets_path)
    with open(os.path.join(story_request.path, "medias.json"), "r") as f:
        medias = json.load(f)
    return [MediaFile(src=media["src"], output=f'current_story/{media["output"]}', text=media["text"]) for media in medias]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
    