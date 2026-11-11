# app.py

import asyncio

from quart import Quart

import db
import ssh
from settings import INTERVAL_SECONDS

app = Quart(__name__)

@app.route("/")
async def index():
    return "test"

async def background_task():
    while True:
        await asyncio.gather(
            ssh.status_check_all(),
            asyncio.sleep(INTERVAL_SECONDS)
        )

@app.before_serving
async def init():
    app.add_background_task(background_task)
    await asyncio.gather(
        db.init(),
    )

