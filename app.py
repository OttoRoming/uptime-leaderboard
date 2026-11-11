# app.py

import asyncio

from quart import Quart
from dotenv import load_dotenv

import db
import ssh

app = Quart(__name__)

@app.route("/")
async def index():
    return "test"

async def background_task():
    while True:
        await asyncio.gather(
            ssh.status_check(),
            asyncio.sleep(60) # seconds
        )

@app.before_serving
async def init():
    load_dotenv()
    app.add_background_task(background_task)
    await asyncio.gather(
        db.init(),
    )

