FROM tiangolo/uvicorn-gunicorn:python3.8-alpine3.10

RUN apk add --no-cache gcc musl-dev

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache -r requirements.txt