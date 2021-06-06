from fastapi import FastAPI, WebSocket
import os
from aio_pika import connect_robust
from aio_pika.patterns import Master, RejectMessage, NackMessage
from starlette.websockets import WebSocketDisconnect
import uvicorn

from notifier import Notifier

RMQ_USER = os.getenv('RMQ_USER') or 'guest'
RMQ_PASSWORD = os.getenv('RMQ_PASSWORD') or 'guest'
RMQ_HOST = os.getenv('RMQ_HOST') or 'localhost'

RANK_PORT = int(os.getenv('RANK_PORT') or '8001')

app = FastAPI()

notifier = Notifier()

@app.get("/")
async def root():
  return {"message": "RANK API is running."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await notifier.connect(websocket)
  try:
    while True:
      data = await websocket.receive_text()
      await websocket.send_text(f"Message text was {data}")
  except WebSocketDisconnect:
    notifier.remove(websocket)


async def new_top_score(*, data: dict):
  await notifier.push(f'{{"score": {data["score"]}}}')
  # print(task_id)

async def create_master():
  connection = await connect_robust(f"amqp://{RMQ_USER}:{RMQ_PASSWORD}@{RMQ_HOST}/")

  channel = await connection.channel()

  master = Master(channel)
  # Publish new top score
  await master.create_worker("ranking", new_top_score)

  return connection

@app.on_event("startup")
async def startup():
    # Prime the push notification generator
    await notifier.generator.asend(None)
    # Create Rabbit MQ Connection
    await create_master()

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=RANK_PORT, )