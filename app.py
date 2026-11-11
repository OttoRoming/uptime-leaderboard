# app.py

import asyncio

from dotenv import load_dotenv
from quart import Quart

import db
import ssh

app = Quart(__name__)

@app.route("/")
async def index():
    return "test"

async def background_task():
    while True:
        await asyncio.gather(
            ssh.status_check_all(),
            asyncio.sleep(60) # seconds
        )

@app.before_serving
async def init():
    load_dotenv()
    app.add_background_task(background_task)
    await asyncio.gather(
        db.init(),
    )

