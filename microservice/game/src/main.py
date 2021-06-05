from fastapi import FastAPI
from aio_pika import connect_robust
from aio_pika.patterns import Master
import uvicorn
import os

from route import router

RMQ_USER = os.getenv('RMQ_USER') or 'guest'
RMQ_PASSWORD = os.getenv('RMQ_PASSWORD') or 'guest'
RMQ_HOST = os.getenv('RMQ_HOST') or 'localhost'

GAME_PORT = int(os.getenv('GAME_PORT') or 8000)

app = FastAPI()
games = []

master = None

app.include_router(router)

@app.get("/")
async def root():
  return {"message": "GAME API is running"}

@app.post("/games")
async def new_game():
  await master.create_task("ranking", kwargs=dict(task_id=20))
  return {"message": "Hello World"}

@app.on_event("startup")
async def startup_event():
  global master 
  master = await create_master()

@app.on_event("shutdown")
async def shutdown_event():
  pass

async def create_master():
  connection = await connect_robust(f"amqp://{RMQ_USER}:{RMQ_PASSWORD}@{RMQ_HOST}/")

  channel = await connection.channel()

  return Master(channel)

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=GAME_PORT, )