# Używamy oficjalnego obrazu Pythona jako obrazu bazowego
FROM python:3.12-slim

# Ustawienie katalogu roboczego w kontenerze
WORKDIR /app

# Pobieranie modeli
RUN pip install sentence-transformers
RUN python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L12-v2');"

RUN pip install FlagEmbedding
RUN python -c "from FlagEmbedding import BGEM3FlagModel; model = BGEM3FlagModel('BAAI/bge-reranker-v2-m3')"

WORKDIR /app

# Kopiowane zaleznosci 
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie reszty aplikacji do obrazu
COPY ./app.py .
COPY ./appconfig.py .
COPY ./session_data.py .
COPY ./api ./api
COPY ./webapp ./webapp

# Ustawienie zmiennej środowiskowej wskazującej na aplikację Flask
ENV FLASK_APP=./app.py

# Inne zmienne środowiskowe
ENV PYTHONUNBUFFERED=1
ENV PATH="$PATH:/home/python/.local/bin"

# Otwarcie portu, na którym aplikacja będzie działać
EXPOSE 8080

# WSGI
RUN pip install gunicorn

CMD [ "gunicorn", "--bind", "0.0.0.0:8080", "app:create_app()", "--workers", "4", "--timeout", "999999" ]
