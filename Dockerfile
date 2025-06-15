FROM ubuntu:22.04

# Pakete installieren
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    curl \
    git \
    build-essential \
    && apt-get clean

# Poetry installieren
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry \

# Arbeitsverzeichnis setzen
WORKDIR /app

# Poetry abhängigkeiten installieren
COPY zpython/pyproject.toml ./
COPY zpython/poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Dateien kopieren
COPY apps/remote-backtest-app/target/remote-backtest-app-1.0-SNAPSHOT.jar app.jar
COPY apps/remote-backtest-app/target/libs/ libs/

COPY zpython/live_prediction python/live_prediction
COPY zpython/model python/model
COPY zpython/util python/util
COPY zpython/japy_starter.py python/japy_starter.py

# Startskript ausführbar machen
RUN chmod +x start.sh

# Starten
CMD ["./start.sh"]
