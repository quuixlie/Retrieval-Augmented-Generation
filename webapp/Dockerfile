# Używamy oficjalnego obrazu Pythona jako obrazu bazowego
FROM python:3.12-slim

# Ustawienie katalogu roboczego w kontenerze
WORKDIR /app

# Tworzenie użytkownika i grupy
ARG UID=1000
ARG GID=1000
RUN set -x && \
    groupadd -g "${GID}" python && \
    useradd --create-home --no-log-init -u "${UID}" -g "${GID}" python &&\
    chown python:python -R /app

USER python

# Kopiowanie pliku requirements.txt i instalacja zależności
COPY requirements.txt /app/

# Instalacja zależności
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie reszty aplikacji do obrazu
COPY . /app/

# Ustawienie zmiennej środowiskowej wskazującej na aplikację Flask
ENV FLASK_APP=app.py

ENV PYTHONUNBUFFERED=1
ENV PATH="$PATH:/home/python/.local/bin"

# Otwarcie portu, na którym aplikacja będzie działać
EXPOSE 5000

# Komenda uruchamiająca aplikację Flask
CMD ["flask", "run", "--host=0.0.0.0"]
