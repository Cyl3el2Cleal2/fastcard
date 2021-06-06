from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from aio_pika import connect_robust
from aio_pika.patterns import Master
import uvicorn
import os

from route import router
from db import connect_db

RMQ_USER = os.getenv('RMQ_USER', 'guest')
RMQ_PASSWORD = os.getenv('RMQ_PASSWORD', 'guest')
RMQ_HOST = os.getenv('RMQ_HOST', 'localhost')

GAME_PORT = int(os.getenv('GAME_PORT', '8000'))

app = FastAPI()

master = None

app.include_router(router)

@app.get("/")
async def root():
  return {"message": "GAME API is running"}

@app.post("/games")
async def new_game():
  await master.create_task("ranking", kwargs=dict(task_id=20))
  return {"message": "Hello World"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)

@app.on_event("startup")
async def startup_event():
  global master 
  master = await create_master()
  await connect_db()

@app.on_event("shutdown")
async def shutdown_event():
  pass

async def create_master():
  try:
    connection = await connect_robust(f"amqp://{RMQ_USER}:{RMQ_PASSWORD}@{RMQ_HOST}/")

    channel = await connection.channel()

    return Master(channel)
  except:
    raise Exception('Can not connect  to RABBITMQ')

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=GAME_PORT, )