from typing import Annotated

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import aiofiles

import os
import sys

app = FastAPI()

SRC_DIR = "./src/app"
STATIC_DIR = f"{SRC_DIR}/static"
TEMP_DIR = f"{SRC_DIR}/upload_dir"
CAT_DIR = f"{STATIC_DIR}/cats"

def hello():
    print("Hello world")

@app.post("/upload_cat")
async def root(
    file: Annotated[UploadFile, File()],
    picture_name: Annotated[str, Form()],
):
    async with aiofiles.open(f"{TEMP_DIR}/tempfile", 'wb') as out_file:
        while content := await file.read(1024):
            await out_file.write(content)
    os.system(f"cp \"{TEMP_DIR}/tempfile\" \"{CAT_DIR}/{picture_name}\".{file.content_type.rsplit('/', 1)[-1]}")
    return RedirectResponse(".", status_code=303)

@app.get("/list_cats")
async def list_cats():
    return os.listdir(f"{STATIC_DIR}/cats")

app.mount("/", StaticFiles(directory="./src/app/static", html = True), name="cat-pics")