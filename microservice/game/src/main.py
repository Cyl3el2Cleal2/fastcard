from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
import uvicorn
import os

from route import router
from db import connect_db
from mq import MQ

RMQ_USER = os.getenv('RMQ_USER', 'guest')
RMQ_PASSWORD = os.getenv('RMQ_PASSWORD', 'guest')
RMQ_HOST = os.getenv('RMQ_HOST', 'localhost')

GAME_PORT = int(os.getenv('GAME_PORT', '8000'))

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

master = None

app.include_router(router, prefix='/api')

@app.get("/")
async def root():
  return {"message": "GAME API is running"}

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
  mq = MQ()
  return await mq.create_master()

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=GAME_PORT, )