# Używamy oficjalnego obrazu Pythona jako obrazu bazowego
FROM python:3.12-slim

# Ustawienie katalogu roboczego w kontenerze
WORKDIR /app

# Instalacja torcha z cpu
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Pobieranie modeli
RUN pip install FlagEmbedding sentence-transformers
RUN python -c "from FlagEmbedding import BGEM3FlagModel; model = BGEM3FlagModel('BAAI/bge-reranker-v2-m3')"
RUN python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L12-v2')"

# Instalacja zależności aplikacji
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie reszty aplikacji do obrazu
COPY . /app/

# Ustawienie zmiennej środowiskowej wskazującej na aplikację Flask
ENV FLASK_APP=app.py

# Zmienna środowiskowa dla konfiguracji PostgreSQL
ENV POSTGRES_HOST=localhost
ENV POSTGRES_PORT=6921
ENV POSTGRES_DB=flaskragdb
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=12345

# Inne zmienne środowiskowe
ENV PYTHONUNBUFFERED=1
ENV PATH="$PATH:/home/python/.local/bin"

# Otwarcie portu, na którym aplikacja będzie działać
EXPOSE 5000

# Komenda uruchamiająca aplikację Flask
CMD ["flask", "run", "--host=0.0.0.0"]
