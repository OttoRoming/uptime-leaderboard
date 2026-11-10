# app.py

from quart import Quart

import db

app = Quart(__name__)


@app.route("/")
async def index():
    return "test"


@app.before_serving
async def init():
    await db.init()
