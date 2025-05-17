FROM python:3.12-slim

WORKDIR /api

RUN apt-get update && apt-get install -y curl

RUN pip install sentence-transformers
RUN python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L12-v2');"

RUN pip install FlagEmbedding
RUN python -c "from FlagEmbedding import BGEM3FlagModel; model = BGEM3FlagModel('BAAI/bge-reranker-v2-m3')"

COPY ./requirements.txt .

run pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1
ENV PATH="$PATH:/home/python/.local/bin"

# Copying rest of the app
COPY . .

RUN pip install fastapi[standard]


CMD [ "uvicorn", "api:create_api", "--factory", "--host", "0.0.0.0","--port", "8080", "--workers", "4" ]
