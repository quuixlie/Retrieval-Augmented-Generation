# Używamy oficjalnego obrazu Pythona jako obrazu bazowego
FROM python:3.12-slim

WORKDIR /app

# Caching models
RUN pip install sentence-transformers
RUN python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L12-v2');"

RUN pip install FlagEmbedding
RUN python -c "from FlagEmbedding import BGEM3FlagModel; model = BGEM3FlagModel('BAAI/bge-reranker-v2-m3')"

COPY ./requirements.txt .

RUN pip install -r requirements.txt

# WSGI
RUN pip install gunicorn

# Copying all files
COPY . .


CMD [ "gunicorn", "--bind", "0.0.0.0:8080", "app:create_app()", "--workers", "4", "--timeout","900" ]
