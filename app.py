# app.py
from quart import Quart
import asyncio

app = Quart(__name__)


@app.route("/")
async def index():
  return "test"

if __name__ == "__main__":
  app.run()
